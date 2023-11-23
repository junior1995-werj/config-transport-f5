import os
import ast
from uuid import uuid4
from datetime import datetime

from flask import flash
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker

from handler.gtm.gtm import GTM
from handler.ltm.ltm import Ltm, LtmMigrate
from handler.utils.utils import Validate, BigIpUtils, UtilsUtils
from handler.big_ip.models import (
    BigIpModel,
    TransportConfigModel,
    TansportConfigImportModel,
)
from handler.system.system import System, SystemMigrate
from handler.big_ip.monitor import Monitor
from handler.network.network import Network, NetworkMigrate
from handler.big_ip.collections import MODELS, IMPORT_CONFIG
from handler.database.connect_db import engine
from handler.ltm.generic_message.generic_message import (
    GenenricMessage,
    GenenricMessageMigrate,
)

big_ip_utils = BigIpUtils()
utils = UtilsUtils()


class BigIpQkView:
    def __init__(self, file, user_import):
        self.session = sessionmaker(bind=engine)
        self.file = file
        self.user_file = None
        self.monitor = Monitor()
        self.id = str(uuid4())
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.mcp_path = os.path.join(self.path, "files/upload/")
        self.qkview_path = os.path.join(self.path, "files")
        self._validate_directory()
        self.system = None
        self.ltm = None
        self.network = None
        self.gm = None
        self.file_xml = None
        self.user_alert = None
        self.user_import = user_import

    def _validate_directory(self):
        if not os.path.exists(self.mcp_path):
            os.mkdir(self.mcp_path)

    def process_file(self):
        self.file_xml, self.user_file, self.user_alert = utils.get_xml_from_qkview(
            self.qkview_path, self.mcp_path, self.file, self.id
        )
        self.monitor.send_status_progres_bar(
            "Arquivos carregados!", status=f"{round((2/35)*100,0)}%"
        )
        flash("Arquivos carregados!")
        self.system = System(
            external_id=self.id,
            file=self.file_xml,
            file_user=self.user_file,
            user_alert=self.user_alert,
        )
        self.ltm = Ltm(external_id=self.id, file=self.file_xml)
        self.network = Network(external_id=self.id, file=self.file_xml)
        self.gtm = GTM(external_id=self.id, file=self.file_xml)
        self.gm = GenenricMessage(external_id=self.id, file=self.file_xml)
        self._create_register_big_ip()
        self._import_system()
        self._import_network()
        self._import_ltm()
        self._import_gtm()
        self._import_gm()
        flash("Processamento Concluido!")

    def _create_register_big_ip(self):
        sessao = self.session()

        system_information = self.system.create_register_database_system_information()
        sys_devices = self.system.create_register_database_sys_device()

        for sys_device in sys_devices:
            if (
                sys_device["chassis_id"]
                == system_information["bigip_chassis_serial_num"]
            ):

                username = "root"
                version = sys_device["version"]
                hostname = sys_device["hostname"]
                bigip_chassis_serial_num = sys_device["chassis_id"]
                ip_management = sys_device["mgmt_ip"]

                dict_value = self.system.get_ntp_snmp_gateway()
                ntp_servers = dict_value["ntp.servers"]
                ntp_timezone = dict_value["ntp.timezone"]
                dns_name_servers = dict_value["dns.nameservers"]
                dns_search = dict_value["dns.domainname"]

                snmp_contact = dict_value["syscontact"]
                snmp_allowed = dict_value["service.snmp.allow"]
                snmp_location = dict_value["syslocation"]
                gateway = dict_value["gateway"]

                big_ip = BigIpModel(
                    id=self.id,
                    host=hostname,
                    password="",
                    username=username,
                    status=True,
                    date_conection=datetime.now(),
                    version=version,
                    hostname=hostname,
                    ntp_servers=ntp_servers,
                    ntp_timezone=ntp_timezone,
                    dns_name_servers=dns_name_servers,
                    dns_search=dns_search,
                    ip_management=ip_management,
                    gateway=gateway,
                    snmp_contact=snmp_contact,
                    snmp_location=snmp_location,
                    snmp_allowed=snmp_allowed,
                    bigip_chassis_serial_num=bigip_chassis_serial_num,
                    user_import=str(self.user_import),
                )

                sessao.add(big_ip)
        sessao.commit()
        sessao.close()
        self.monitor.send_status_progres_bar(
            "Informações do big_ip Carregadas", status=f"{round((3/35)*100,2)}%"
        )

    def _import_system(self):
        self.monitor.send_status_progres_bar(
            "create_register_database_folder", status=f"{round((4/35)*100,2)}%"
        )
        self.system.create_register_database_folder()
        self.monitor.send_status_progres_bar(
            "create_register_database_system_module", status=f"{round((5/35)*100,2)}%"
        )
        self.system.create_register_database_system_module()
        self.monitor.send_status_progres_bar(
            "create_register_database_icall", status=f"{round((6/35)*100,2)}%"
        )
        self.system.create_register_database_icall()
        self.monitor.send_status_progres_bar(
            "create_register_database_chassis", status=f"{round((7/35)*100,2)}%"
        )
        self.system.create_register_database_chassis()
        self.monitor.send_status_progres_bar(
            "create_register_database_traffic_group", status=f"{round((8/35)*100,2)}%"
        )
        self.system.create_register_database_traffic_group()
        self.monitor.send_status_progres_bar(
            "create_register_database_users", status=f"{round((9/35)*100,2)}%"
        )
        self.system.create_register_database_users()
        self.monitor.send_status_progres_bar(
            "create_register_database_user_alert", status=f"{round((10/35)*100,2)}%"
        )
        self.system.create_register_database_user_alert()

    def _import_network(self):
        self.network.create_register_vlans()
        self.monitor.send_status_progres_bar(
            "create_register_vlans", status=f"{round((11/35)*100,2)}%"
        )
        self.network.create_register_trunks()
        self.monitor.send_status_progres_bar(
            "create_register_trunks", status=f"{round((12/35)*100,2)}%"
        )
        self.network.create_register_static_route()
        self.monitor.send_status_progres_bar(
            "create_register_static_route", status=f"{round((13/35)*100,2)}%"
        )
        self.network.create_register_self_ip()
        self.monitor.send_status_progres_bar(
            "create_register_self_ip", status=f"{round((14/35)*100,2)}%"
        )
        self.network.create_register_routes_domains()
        self.monitor.send_status_progres_bar(
            "create_register_routes_domains", status=f"{round((15/35)*100,2)}%"
        )
        self.network.create_register_packet_filters_rule()
        self.monitor.send_status_progres_bar(
            "create_register_packet_filters_rule", status=f"{round((16/35)*100,2)}%"
        )

    def _import_ltm(self):
        self.ltm.create_register_database_pool_and_members()
        self.monitor.send_status_progres_bar(
            "create_register_database_pool_and_members",
            status=f"{round((17/35)*100,2)}%",
        )
        self.ltm.create_register_database_virtual_server()
        self.monitor.send_status_progres_bar(
            "create_register_database_virtual_server", status=f"{round((18/35)*100,2)}%"
        )
        self.ltm.create_register_database_irule_and_datagroups()
        self.monitor.send_status_progres_bar(
            "create_register_database_irule_and_datagroups",
            status=f"{round((19/35)*100,2)}%",
        )
        self.ltm.create_register_database_monitor()
        self.monitor.send_status_progres_bar(
            "create_register_database_monitor", status=f"{round((20/35)*100,2)}%"
        )
        self.ltm.create_register_database_nat()
        self.monitor.send_status_progres_bar(
            "create_register_database_nat", status=f"{round((21/35)*100,2)}%"
        )
        self.ltm.create_register_database_snat_pool()
        self.monitor.send_status_progres_bar(
            "create_register_database_snat_pool", status=f"{round((22/35)*100,2)}%"
        )
        self.ltm.create_register_database_policies()
        self.monitor.send_status_progres_bar(
            "create_register_database_policies", status=f"{round((23/35)*100,2)}%"
        )
        self.ltm.create_register_database_profiles()
        self.monitor.send_status_progres_bar(
            "create_register_database_profiles", status=f"{round((24/35)*100,2)}%"
        )
        self.ltm.create_register_database_snat()
        self.monitor.send_status_progres_bar(
            "create_register_database_snat", status=f"{round((25/35)*100,2)}%"
        )

    def _import_gtm(self):
        self.gtm.create_register_database_datacenter()
        self.monitor.send_status_progres_bar(
            "create_register_database_datacenter", status=f"{round((26/35)*100,2)}%"
        )
        self.gtm.create_register_database_server_gtm()
        self.monitor.send_status_progres_bar(
            "create_register_database_server_gtm", status=f"{round((27/35)*100,2)}%"
        )
        self.gtm.create_register_database_server_ip()
        self.monitor.send_status_progres_bar(
            "create_register_database_server_ip", status=f"{round((28/35)*100,2)}%"
        )
        self.gtm.create_register_database_wide_ip()
        self.monitor.send_status_progres_bar(
            "create_register_database_wide_ip", status=f"{round((29/35)*100,2)}%"
        )
        self.gtm.create_register_database_pool_wide_ip()
        self.monitor.send_status_progres_bar(
            "create_register_database_pool_wide_ip", status=f"{round((30/35)*100,2)}%"
        )

    def _import_gm(self):
        self.gm.create_register_peer()
        self.monitor.send_status_progres_bar(
            "create_register_peer", status=f"{round((31/35)*100,2)}%"
        )
        self.gm.create_register_protocol()
        self.monitor.send_status_progres_bar(
            "create_register_protocol", status=f"{round((32/35)*100,2)}%"
        )
        self.gm.create_register_route()
        self.monitor.send_status_progres_bar(
            "create_register_route", status=f"{round((33/35)*100,2)}%"
        )
        self.gm.create_register_router()
        self.monitor.send_status_progres_bar(
            "create_register_router", status=f"{round((34/35)*100,2)}%"
        )
        self.gm.create_register_transport_config()
        self.monitor.send_status_progres_bar(
            "Concluido", status=f"{round((35/35)*100,2)}%"
        )


class BigIpProcess:
    def __init__(self):
        self.monitor = Monitor()
        self.session = sessionmaker(bind=engine)
        self.ltm = Ltm()

    def get_connections(self):
        sessao = self.session()
        result_query = sessao.query(BigIpModel).filter(BigIpModel.status).all()
        sessao.close()
        list_connections = []
        for result in result_query:
            list_connections.append(
                {
                    "id": result.id,
                    "username": result.username,
                    "status": result.status,
                    "date_conection": result.date_conection,
                    "host": result.host,
                    "user_import": result.user_import,
                }
            )
        return list_connections

    def get_connection_by_id(self, id):
        sessao = self.session()
        result_query = sessao.query(BigIpModel).filter(BigIpModel.id == id).first()
        sessao.close()
        data = {
            "host": result_query.host,
            "username": result_query.username,
            "id": str(result_query.id),
            "date_conection": result_query.date_conection,
            "version": result_query.version,
            "hostname": result_query.hostname,
            "ntp_servers": result_query.ntp_servers,
            "ntp_timezone": result_query.ntp_timezone,
            "dns_name_servers": result_query.dns_name_servers,
            "dns_search": result_query.dns_search,
            "ip_management": result_query.ip_management,
            "gateway": result_query.gateway,
            "snmp_contact": result_query.snmp_contact,
            "snmp_location": result_query.snmp_location,
            "snmp_allowed": result_query.snmp_allowed,
        }
        return data

    def delete_connection(self, id):
        sessao = self.session()
        big_ip = sessao.query(BigIpModel).filter(BigIpModel.id == id).first()
        big_ip.status = False
        sessao.add(big_ip)
        sessao.commit()
        sessao.close()


class TransportConfig:
    def __init__(self, host=None, username=None, password=None):
        self.session = sessionmaker(bind=engine)
        self.monitor = Monitor()
        self.host = host
        self.username = username
        self.password = password
        self.system = System()
        self.ltm = Ltm()
        self.network = Network()
        self.gtm = GTM()
        self.validate = Validate()

    def insert(self, internal_id, external_id, service, all=False):
        id = str(uuid4())
        sessao = self.session()
        result_find = (
            sessao.query(TransportConfigModel)
            .filter(
                and_(
                    TransportConfigModel.internal_id == internal_id,
                    TransportConfigModel.external_id == external_id,
                    TransportConfigModel.service == service,
                ),
            )
            .first()
        )

        if not result_find:
            models_query = (
                sessao.query(MODELS[service])
                .filter(MODELS[service].id == internal_id)
                .first()
            )
            dict_models = models_query.__dict__
            dict_models.pop("_sa_instance_state")
            transport_config = TransportConfigModel(
                id=id,
                internal_id=internal_id,
                external_id=external_id,
                service=service,
                data=str(dict_models),
                imported_configuration=False,
            )
            sessao.add(transport_config)

            self.monitor.new_add_config_header(
                service, internal_id, external_id, id, dict_models, all
            )

            sessao.commit()
            sessao.close()

        else:
            if not all:
                self.monitor.send_return_alert("Item adicionado!")

    def update(self, data):
        sessao = self.session()
        result_find = (
            sessao.query(TransportConfigModel)
            .filter(
                and_(
                    TransportConfigModel.external_id == data["external_id"],
                    TransportConfigModel.service == data["service"],
                    TransportConfigModel.internal_id == data["id"],
                ),
            )
            .first()
        )
        data = dict(data)
        data.pop("service")
        result_find.data = str(data)
        sessao.add(result_find)
        sessao.commit()
        sessao.close()

    def insert_all(self, external_id, service):
        id = str(uuid4())
        sessao = self.session()
        result_find = (
            sessao.query(TransportConfigModel)
            .filter(
                and_(
                    TransportConfigModel.external_id == external_id,
                    TransportConfigModel.service == service,
                ),
            )
            .all()
        )
        if not result_find:
            models_query = (
                sessao.query(MODELS[service])
                .filter(MODELS[service].external_id == external_id)
                .all()
            )

            for model in models_query:
                self.insert(str(model.id), model.external_id, service, True)

            self.monitor.send_return_alert("Item adicionado!", True)
        else:
            sessao.query(TransportConfigModel).filter(
                and_(
                    TransportConfigModel.external_id == external_id,
                    TransportConfigModel.service == service,
                ),
            ).delete()
            transport_config = TransportConfigModel(
                id=id,
                internal_id="1an23",
                external_id=external_id,
                service=service,
                data=str({"name": "all-config"}),
                imported_configuration=False,
            )
            sessao.add(transport_config)
            self.monitor.new_add_config_header(
                service, "1an23", external_id, id, {"name": "all-config"}
            )
            sessao.commit()
            sessao.close()

    def insert_by_filter(self, message: dict):
        dados = message["dados"]
        service = message["service"]

        for dado in dados:
            self.insert(
                internal_id=dado["id"],
                external_id=dado["external_id"],
                service=service,
                all=True,
            )

        self.monitor.send_return_alert("Item adicionado!", True)

    def insert_default_config(self, message: dict):
        id = str(uuid4())
        sessao = self.session()
        result_find = (
            sessao.query(TransportConfigModel)
            .filter(
                and_(
                    TransportConfigModel.internal_id == message["id"],
                    TransportConfigModel.external_id == message["id"],
                    TransportConfigModel.service == "default",
                ),
            )
            .first()
        )

        if not result_find:
            message["comand"] = "sem comando criado"
            transport_config = TransportConfigModel(
                id=id,
                internal_id=message["id"],
                external_id=message["id"],
                service="default",
                data=str(message),
                imported_configuration=False,
            )
            sessao.add(transport_config)
            self.monitor.new_add_config_header(
                "default", message["id"], message["id"], id, message
            )
            sessao.commit()
            sessao.close()

        else:
            self.monitor.send_return_alert("Objeto ja insserido!")

    def delete(self, internal_id=None, external_id=None, id=None, service=None):
        sessao = self.session()
        if id:
            sessao.query(TransportConfigModel).filter(
                TransportConfigModel.id == id
            ).delete()
        else:
            sessao.query(TransportConfigModel).filter(
                and_(
                    TransportConfigModel.internal_id == internal_id,
                    TransportConfigModel.external_id == external_id,
                    TransportConfigModel.service == service,
                ),
            ).delete()
        sessao.commit()
        sessao.close()

        self.get_transport_config(external_id=external_id, internal=True)

    def get_transport_config(self, external_id, internal=False):
        sessao = self.session()
        validate = False
        result_query = (
            sessao.query(TransportConfigModel)
            .filter(
                and_(
                    TransportConfigModel.external_id == str(external_id),
                    TransportConfigModel.imported_configuration == validate,
                ),
            )
            .all()
        )
        # validar aqui

        data = []
        for result in result_query:
            model = ast.literal_eval(result.data)
            if result.internal_id == "1an23":
                result_query = (
                    sessao.query(MODELS[result.service])
                    .filter(MODELS[result.service].external_id == str(external_id))
                    .all()
                )
                for query in result_query:
                    dict_models = query.__dict__
                    dict_models.pop("_sa_instance_state")
                    data.append(
                        {
                            "service": result.service,
                            "name": dict_models["name"],
                            "external_id": result.external_id,
                            "internal_id": result.internal_id,
                            "id": result.id,
                            "model": dict_models,
                            "imported_configuration": result.imported_configuration,
                        }
                    )
            else:
                data.append(
                    {
                        "service": result.service,
                        "name": model["name"],
                        "external_id": result.external_id,
                        "internal_id": result.internal_id,
                        "id": result.id,
                        "model": model,
                    }
                )

        if internal:
            self.monitor.get_all_config_add_header(data)
            return

        return data

    def get_finish_services_with_comands(self, external_id: str):
        transport_configs = self.get_transport_config(external_id=external_id)
        transport_configs = sorted(
            transport_configs, key=lambda dicionario: dicionario["service"]
        )
        services = {x["service"] for x in transport_configs}

        list_return = {}
        for service in services:
            list_service = []
            for transport_config in transport_configs:
                if transport_config["service"] == service:
                    if service != "default":
                        transport_config["model"].pop("external_id")
                    list_service.append(transport_config["model"])
            list_return[service] = list_service

        list_return_errors = self.validate.validate(list_return)

        return list_return, list_return_errors

    def get_configs_import(self, external_id):
        sessao = self.session()
        result_query = (
            sessao.query(TansportConfigImportModel)
            .filter(TansportConfigImportModel.external_id == str(external_id))
            .all()
        )

        data = []
        for result in result_query:
            data.append(
                {
                    "status": result.status,
                    "reason": result.reason,
                    "service": result.service,
                    "payload": result.data,
                    "date_import": result.date_import,
                }
            )
        return data


class TansportConfigImport(TransportConfig):
    def __init__(self, external_id, host, username, password, user_migrate):
        super().__init__()
        self.external_id = external_id
        self.host = host
        self.user = username
        self.password = password
        self.user_migrate = user_migrate
        self.session = sessionmaker(bind=engine)

        self.ltm = LtmMigrate(
            external_id=self.external_id,
            host=self.host,
            username=self.user,
            password=self.password,
            user_migrate=self.user_migrate,
        )
        self.netowrk = NetworkMigrate(
            external_id=self.external_id,
            host=self.host,
            username=self.user,
            password=self.password,
            user_migrate=self.user_migrate,
        )
        self.gm = GenenricMessageMigrate(
            external_id=self.external_id,
            host=self.host,
            username=self.user,
            password=self.password,
            user_migrate=self.user_migrate,
        )
        self.system = SystemMigrate(
            external_id=self.external_id,
            host=self.host,
            username=self.user,
            password=self.password,
            user_migrate=self.user_migrate,
        )

    def start(self):
        execute = self.get_transport_config(self.external_id)
        services = {x["service"] for x in execute}
        services = self._define_priority(services=services)
        self._execute(services, execute)

    def _find_metod_to_execute(self, service):
        dict_metod = {
            "nat": self.ltm.create_nat,
            "snat": self.ltm.create_snat,
            "snat_pool": self.ltm.create_snat_pool,
            "profiles_ssl": self.ltm.create_profile_ssl,
            "profiles_services": self.ltm.create_profile_services,
            "profiles_persist": self.ltm.create_profile_persist,
            "profiles_other": self.ltm.create_profile_other,
            "profiles_protocol": self.ltm.create_profile_protocol,
            "policies": self.ltm.create_policies,
            "monitor": self.ltm.create_monitor,
            "datagroup": self.ltm.create_datagroup,
            "irule": self.ltm.create_irule,
            "pool": self.ltm.create_pool,
            "virtual_server": self.ltm.create_virtual_server,
            "vlan": self.netowrk.create_vlan,
            "trunks": self.netowrk.create_trunks,
            "self_ip": self.netowrk.create_self_ip,
            "static_route": self.netowrk.create_static_route,
            "peer": self.gm.create_peer,
            "protocol": self.gm.create_protocol,
            "route": self.gm.create_route,
            "router": self.gm.create_router,
            "transport_config": self.gm.create_gm_transport_config,
            "user_alert": self.system.import_user_alert,
            "icall": self.system.import_icall,
            "traffic_group": self.system.import_traffic_group,
            "route_domain": self.netowrk.create_route_domain,
            "folder": self.system.import_folder,
            "default": self.system.craeate_default_configuration,
        }
        return dict_metod[service]

    def _get_itens_to_execute(self, service, execute):
        list_return = []
        for item in execute:
            if item["service"] == service:
                list_return.append(item)
            else:
                continue
        return list_return

    def _define_priority(self, services):
        dict_priority = {}
        for service in services:
            if IMPORT_CONFIG[service] not in dict_priority.keys():
                dict_priority[IMPORT_CONFIG[service]] = []
                dict_priority[IMPORT_CONFIG[service]].append(service)
            else:
                dict_priority[IMPORT_CONFIG[service]].append(service)
        return dict_priority

    def _update_transport_config_send_config(self):
        sessao = self.session()
        result_query = (
            sessao.query(TransportConfigModel)
            .filter(TransportConfigModel.external_id == str(self.external_id))
            .all()
        )
        for itens in result_query:
            itens.imported_configuration = True
            sessao.add(itens)
        sessao.commit()
        sessao.close()

    def _execute(self, priority_services, execute):
        find_priority = sorted(priority_services)

        for priority in find_priority:
            list_services_by_priorty = priority_services[priority]
            for item in list_services_by_priorty:
                method_execute = self._find_metod_to_execute(item)
                itens_execute = self._get_itens_to_execute(item, execute)
                method_execute(itens_execute)

        self._update_transport_config_send_config()


class TansportConfigComands(TransportConfig):
    def __init__(self, external_id):
        super().__init__()
        self.external_id = external_id
        self.session = sessionmaker(bind=engine)

    def start(self):
        execute = self.get_transport_config(self.external_id)
        services = {x["service"] for x in execute}
        services = self._define_priority(services=services)
        return self._execute(services, execute)

    def _get_itens_to_execute(self, service, execute):
        list_return = []
        for item in execute:
            if item["service"] == service:
                if "comand" not in item["model"].keys():
                    item["model"]["comand"] = "sem comando!"
                list_return.append(item["model"]["comand"])
            else:
                continue
        return list_return

    def _define_priority(self, services):
        dict_priority = {}
        for service in services:
            if IMPORT_CONFIG[service] not in dict_priority.keys():
                dict_priority[IMPORT_CONFIG[service]] = []
                dict_priority[IMPORT_CONFIG[service]].append(service)
            else:
                dict_priority[IMPORT_CONFIG[service]].append(service)
        return dict_priority

    def _execute(self, priority_services, execute):
        list_comands = []
        find_priority = sorted(priority_services)

        for priority in find_priority:
            list_services_by_priorty = priority_services[priority]
            for item in list_services_by_priorty:
                list_comands.extend([f"#------------{item.upper()}------------#"])
                itens_execute = self._get_itens_to_execute(item, execute)
                list_comands.extend(itens_execute)
                list_comands.extend([" "])

        return list_comands
