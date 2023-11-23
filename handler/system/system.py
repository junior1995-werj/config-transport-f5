import os
import re
import json
import time
from datetime import datetime

import paramiko
import requests
from netmiko import ConnectHandler
from sqlalchemy.orm import sessionmaker

from handler.utils.utils import UtilsUtils
from handler.big_ip.models import TansportConfigImportModel
from handler.system.models import (
    UserModel,
    FolderModel,
    ChassisModel,
    SysDeviceModel,
    UserAlertModel,
    DevicegroupModel,
    SystemModuleModel,
    TrafficGroupModel,
    SystemInformationModel,
    iCallModel,
)
from handler.big_ip.monitor import Monitor
from handler.database.connect_db import engine

utils = UtilsUtils()
monitor_big = Monitor()


class System:
    def __init__(
        self,
        external_id=None,
        host=None,
        username=None,
        password=None,
        file=None,
        file_user=None,
        user_alert=None,
    ):
        self._host = host
        self._username = username
        self._password = password
        self.net_connect = None
        self.external_id = external_id
        self.ssh = False
        self.file = file
        self.file_user = file_user
        self.user_alert = user_alert
        if self._username and self._password and self._host and self.external_id:
            self.connect()
        self.session = sessionmaker(bind=engine)

    def connect(self):
        try:
            big_ip = {
                "device_type": "f5_tmsh",
                "host": self._host,
                "username": self._username,
                "password": self._password,
            }
            self.net_connect = ConnectHandler(**big_ip)
            self.ssh = True
            return True
        except Exception:
            return False

    def create_register_database_system_information(self):
        sessao = self.session()
        root_key = "system_information"
        child_keys_list = [
            "platform",
            "host_board_serial_num",
            "bigip_chassis_serial_num",
        ]
        system_info = utils.json_parser(self.file, root_key, child_keys_list)
        data = SystemInformationModel(**system_info[0], external_id=self.external_id)

        sessao.add(data)
        sessao.commit()
        sessao.close()
        return system_info[0]

    def get_static_system_information_by_id(self, external_id):
        sessao = self.session()
        system_infos = (
            sessao.query(SystemInformationModel)
            .filter(SystemInformationModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_system_infos = []

        for system_info in system_infos:
            list_system_infos.append(
                {
                    "id": system_info.id,
                    "platform": system_info.platform,
                    "host_board_serial_num": system_info.host_board_serial_num,
                    "bigip_chassis_serial_num": system_info.bigip_chassis_serial_num,
                    "external_id": system_info.external_id,
                }
            )
        return list_system_infos

    def create_register_database_devicegroup(self):
        sessao = self.session()
        root_key = "devicegroup"
        child_keys_list = [
            "leaf_name",
            "incremental_config_sync_size_max",
            "type",
            "autosync_enabled",
            "failover_state",
            "network_failover_enabled",
        ]
        devicegroups = utils.json_parser(self.file, root_key, child_keys_list)

        for devicegroup in devicegroups:
            data = DevicegroupModel(**devicegroup, external_id=self.external_id)
            sessao.add(data)

        sessao.commit()
        sessao.close()

    def get_static_devicegroup_by_id(self, external_id):
        sessao = self.session()
        devicegroups = (
            sessao.query(DevicegroupModel)
            .filter(DevicegroupModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_devicegroups = []

        for devicegroup in devicegroups:
            list_devicegroups.append(
                {
                    "id": devicegroup.id,
                    "name": devicegroup.name,
                    "network_failover_enabled": devicegroup.network_failover_enabled,
                    "autosync_enabled": devicegroup.autosync_enabled,
                    "external_id": devicegroup.external_id,
                }
            )
        return list_devicegroups

    def create_register_database_folder(self):
        sessao = self.session()
        root_key = "folder"
        child_keys_list = ["leaf_name", "devicegroup", "traffic_group"]
        folders = utils.json_parser(self.file, root_key, child_keys_list)

        for folder in folders:
            if folder["leaf_name"] not in ["/", "Common", "Drafts"]:
                data = FolderModel(**folder, external_id=self.external_id)
                sessao.add(data)
            else:
                continue
        sessao.commit()
        sessao.close()

    def get_static_folder_by_id(self, external_id):
        sessao = self.session()
        folders = (
            sessao.query(FolderModel)
            .filter(FolderModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_folders = []

        for folder in folders:
            list_folders.append(
                {
                    "id": folder.id,
                    "folder_name": folder.name,
                    "devicegroup": folder.devicegroup,
                    "traffic_group": folder.traffic_group,
                    "external_id": folder.external_id,
                }
            )
        return list_folders

    def create_register_database_system_module(self):
        sessao = self.session()
        root_key = "system_module"
        child_keys_list = [
            "display_name",
            "provision_level",
            "licensed",
            "expiration_date",
        ]
        system_modules = utils.json_parser(self.file, root_key, child_keys_list)

        for system_module in system_modules:
            data = SystemModuleModel(**system_module, external_id=self.external_id)
            sessao.add(data)

        sessao.commit()
        sessao.close()

    def get_static_system_module_by_id(self, external_id):
        sessao = self.session()
        system_modules = (
            sessao.query(SystemModuleModel)
            .filter(SystemModuleModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_system_modules = []

        for system_module in system_modules:
            list_system_modules.append(
                {
                    "id": system_module.id,
                    "name": system_module.name,
                    "provision_level": system_module.provision_level,
                    "licensed": system_module.licensed,
                    "expiration_date": system_module.expiration_date,
                    "external_id": system_module.external_id,
                }
            )
        return list_system_modules

    def create_register_database_sys_device(self):
        sessao = self.session()
        root_key = "sys_device"
        child_keys_list = [
            "hostname",
            "chassis_id",
            "mgmt_ip",
            "configsync_ip",
            "failover_state",
            "version",
            "edition",
            "build",
            "timezone",
        ]
        sys_devices = utils.json_parser(self.file, root_key, child_keys_list)

        for sys_device in sys_devices:
            data = SysDeviceModel(**sys_device, external_id=self.external_id)
            sessao.add(data)

        sessao.commit()
        sessao.close()
        return sys_devices

    def get_static_sys_device_by_id(self, external_id):
        sessao = self.session()
        sys_devices = (
            sessao.query(SysDeviceModel)
            .filter(SysDeviceModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_sys_devices = []

        for sys_device in sys_devices:
            list_sys_devices.append(
                {
                    "id": sys_device.id,
                    "hostname": sys_device.hostname,
                    "chassis_id": sys_device.chassis_id,
                    "mgmt_ip": sys_device.mgmt_ip,
                    "configsync_ip": sys_device.configsync_ip,
                    "failover_state": sys_device.failover_state,
                    "version": sys_device.version,
                    "edition": sys_device.edition,
                    "build": sys_device.build,
                    "timezone": sys_device.timezone,
                    "external_id": sys_device.external_id,
                }
            )
        return list_sys_devices

    def create_register_database_icall(self):
        sessao = self.session()
        root_key = "icall_script"
        child_keys_list = ["name", "definition"]
        icalls = utils.json_parser(self.file, root_key, child_keys_list)

        root_key = "icall_triggered_handler"
        child_keys_list = ["leaf_name"]
        icall_triggered = utils.json_parser(self.file, root_key, child_keys_list)

        root_key = "icall_periodic_handler"
        child_keys_list = ["leaf_name"]
        icall_periodics = utils.json_parser(self.file, root_key, child_keys_list)

        root_key = "icall_perpetual_handler"
        child_keys_list = ["leaf_name"]
        icall_perpetuals = utils.json_parser(self.file, root_key, child_keys_list)

        for icall in icalls:
            name = icall["name"].replace("/Common/", "")
            for icall_type in icall_triggered:
                if icall_type["leaf_name"] == name:
                    icall["type_icall"] = "icall_triggered"
            for icall_perpetual in icall_perpetuals:
                if icall_perpetual["leaf_name"] == name:
                    icall["type_icall"] = "icall_perpetual"
            for icall_periodic in icall_periodics:
                if icall_periodic["leaf_name"] == name:
                    icall["type_icall"] = "icall_periodic"

            data = iCallModel(**icall, external_id=self.external_id)
            sessao.add(data)

        sessao.commit()
        sessao.close()

    def get_static_icall_by_id(self, external_id):
        sessao = self.session()
        icalls = (
            sessao.query(iCallModel)
            .filter(iCallModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_icalls = []

        for icall in icalls:
            list_icalls.append(
                {
                    "id": icall.id,
                    "name": icall.name,
                    "type_icall": icall.type_icall,
                    "definition": icall.definition,
                    "external_id": icall.external_id,
                }
            )
        return list_icalls

    def create_register_database_chassis(self):
        sessao = self.session()
        root_key = "chassis"
        child_keys_list = ["marketing_name", "serial_num", "reg_key"]
        chassis = utils.json_parser(self.file, root_key, child_keys_list)

        for chassi in chassis:
            data = ChassisModel(**chassi, external_id=self.external_id)
            sessao.add(data)

        sessao.commit()
        sessao.close()

    def get_static_chassis_by_id(self, external_id):
        sessao = self.session()
        chassis = (
            sessao.query(ChassisModel)
            .filter(ChassisModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_chassis = []

        for chassi in chassis:
            list_chassis.append(
                {
                    "id": chassi.id,
                    "name": chassi.name,
                    "serial_num": chassi.serial_num,
                    "reg_key": chassi.reg_key,
                    "external_id": chassi.external_id,
                }
            )
        return list_chassis

    def create_register_database_traffic_group(self):
        sessao = self.session()
        root_key = "traffic_group"
        child_keys_list = ["partition_id", "leaf_name", "failover_method"]
        traffic_groups = utils.json_parser(self.file, root_key, child_keys_list)

        dict_failover = {
            "1": "ha-score",
            "2": "ha-order",
            None: "ha-order",
        }

        for traffic_group in traffic_groups:
            if traffic_group["leaf_name"] not in [
                "traffic-group-1",
                "traffic-group-local-only",
            ]:
                traffic_group["name"] = traffic_group["leaf_name"]
                del traffic_group["leaf_name"]
                traffic_group["failover_method"] = dict_failover[
                    traffic_group["failover_method"]
                ]
                data = TrafficGroupModel(**traffic_group, external_id=self.external_id)
                sessao.add(data)

        sessao.commit()
        sessao.close()

    def get_static_traffic_group_by_id(self, external_id):
        sessao = self.session()
        traffic_groups = (
            sessao.query(TrafficGroupModel)
            .filter(TrafficGroupModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_traffic_groups = []

        for traffic_group in traffic_groups:
            list_traffic_groups.append(
                {
                    "id": traffic_group.id,
                    "partition_id": traffic_group.partition_id,
                    "name": traffic_group.name,
                    "failover_state": traffic_group.failover_method,
                    "external_id": traffic_group.external_id,
                }
            )
        return list_traffic_groups

    def create_register_database_users(self):
        sessao = self.session()
        # Abrir o arquivo
        while self.file_user:
            user = re.search(r"auth user (\w+)", self.file_user)
            if user:
                user = user.group(1)
                description = ""
                session_limit = ""
                role = ""
                print("User: " + user)
                match = re.search(
                    r"auth user " + user + r" {([\s\S]*?)\n}", self.file_user
                )
                # Extrair valores usando expressões regulares
                teste = match.group(1)
                description_match = re.search(r"description (\w+)", teste)
                if description_match:
                    description = description_match.group(1)
                    print(f"Descrição: {description}")
                role_match = re.search(r"role (\w+)", teste)
                if role_match:
                    role = role_match.group(1)
                    print(f"Função: {role}")

                session_limit_match = re.search(r"session-limit (-?\d+)", teste)
                if session_limit_match:
                    session_limit = session_limit_match.group(1)
                    print(f"Limite de sessão: {session_limit}")

                self.file_user = self.file_user.replace(match.group(0), "")

                sessao.add(
                    UserModel(
                        name=user,
                        description=description,
                        limit_session=session_limit,
                        role=role,
                        external_id=self.external_id,
                    )
                )
            else:
                break

        sessao.commit()
        sessao.close()

    def get_static_users_by_id(self, external_id):
        sessao = self.session()
        users = (
            sessao.query(UserModel)
            .filter(UserModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_users = []

        for user in users:
            list_users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "description": user.description,
                    "limit_session": user.limit_session,
                    "role": user.role,
                    "external_id": user.external_id,
                }
            )
        return list_users

    def create_register_database_user_alert(self):
        sessao = self.session()
        sessao.add(
            UserAlertModel(
                name="user_alert",
                user_alert=self.user_alert,
                external_id=self.external_id,
            )
        )
        sessao.commit()
        sessao.close()

    def get_user_alert_by_id(self, external_id):
        sessao = self.session()
        user_alert = (
            sessao.query(UserAlertModel)
            .filter(UserAlertModel.external_id == str(external_id))
            .first()
        )
        sessao.close()
        list_users = []

        list_users.append(
            {
                "id": user_alert.id,
                "name": user_alert.name,
                "user_alert": user_alert.user_alert,
                "external_id": user_alert.external_id,
            }
        )

        return list_users

    def get_ntp_snmp_gateway(self):
        root_key = "db_variable"
        child_keys_list = ["name", "value"]
        db_variables = utils.json_parser(self.file, root_key, child_keys_list)

        key_db_variables = [
            "dns.nameservers",
            "dns.domainname",
            "ntp.servers",
            "ntp.timezone",
            "service.snmp.allow",
            "syscontact",
            "syslocation",
        ]

        dict_value = {}
        for db_variable in db_variables:
            if db_variable["name"] in key_db_variables:
                dict_value[db_variable["name"]] = db_variable["value"]

        root_key = "ltcfg_instance_field"
        child_keys_list = ["field_name", "value"]
        ltcfg_fields = utils.json_parser(self.file, root_key, child_keys_list)

        for ltcfg_field in ltcfg_fields:
            if ltcfg_field["field_name"] in key_db_variables:
                dict_value[ltcfg_field["field_name"]] = ltcfg_field["value"]

        if "syscontact" not in dict_value.keys():
            dict_value["syscontact"] = "Customer Name <admin@customer.com>"
        if "syslocation" not in dict_value.keys():
            dict_value["syslocation"] = "Network Closet 1"

        root_key = "route_mgmt_entry"
        child_keys_list = ["gateway"]
        ltcfg_fields = utils.json_parser(self.file, root_key, child_keys_list)
        if ltcfg_fields:
            dict_value["gateway"] = ltcfg_fields[0]["gateway"]
        else:
            dict_value["gateway"] = ""

        return dict_value


class SystemMigrate:
    def __init__(self, host, username, password, external_id, user_migrate):
        self.host = host
        self.port = 22
        self.username = username
        self.password = password
        self.external_id = external_id
        self.db = sessionmaker(bind=engine)
        self.user_migrate = user_migrate

    def _save_register(self, payload, internal_id, status_code, reason, service):
        db = self.db()
        db.add(
            TansportConfigImportModel(
                internal_id=internal_id,
                data=str(payload),
                external_id=self.external_id,
                date_import=datetime.now(),
                status=str(status_code),
                reason=reason,
                service=service,
                username=self.user_migrate,
            ),
        )
        db.commit()
        db.close()

    def import_user_alert(self, data):
        self.path = os.path.dirname(os.path.realpath("big_ip"))
        self.mcp_path = os.path.join(
            self.path, f"handler/big_ip/files/upload/{data[0]['external_id']}"
        )
        client = paramiko.SSHClient()
        src_file = os.path.join(self.mcp_path, "user_alert.conf")
        dest_file = "/config/user_alert.conf"

        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.host, self.port, self.username, self.password)

        sftp = client.open_sftp()
        sftp.put(src_file, dest_file)
        sftp.close()

        self._save_register(
            payload="ok",
            internal_id=data[0]["model"]["id"],
            status_code="200",
            reason="Arquivo enviado via SSH enviado!",
            service="user_alert",
        )
        monitor_big.send_status_process_import(
            status=200,
            service="pool",
            name_service="user_alert",
            reason="Arquivo enviado via SSH enviado!",
        )

        client.close()

    def import_icall(self, list_icall):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for icall in list_icall:
            payload = {
                "name": icall["model"]["name"],
                "definition": icall["model"]["definition"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/sys/icall/script",
                data=json.dumps(payload),
            )

            if icall["model"]["type_icall"] == "icall_triggered":
                payload = {
                    "name": icall["model"]["name"],
                    "script": icall["model"]["name"],
                }
                result = session.post(
                    f"https://{self.host}/mgmt/tm/sys/icall/handler/triggered/",
                    data=json.dumps(payload),
                )
            elif icall["model"]["type_icall"] == "icall_perpetual":
                payload = {
                    "name": icall["model"]["name"],
                    "script": icall["model"]["name"],
                }
                result = session.post(
                    f"https://{self.host}/mgmt/tm/sys/icall/handler/perpetual/",
                    data=json.dumps(payload),
                )

            elif icall["model"]["type_icall"] == "icall_periodic":
                payload = {
                    "name": icall["model"]["name"],
                    "script": icall["model"]["name"],
                }
                result = session.post(
                    f"https://{self.host}/mgmt/tm/sys/icall/handler/periodic/",
                    data=json.dumps(payload),
                )

            else:
                continue

            self._save_register(
                payload=payload,
                internal_id=icall["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="icall",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="icall",
                name_service=icall["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def import_traffic_group(self, list_traffic_group):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for traffic_group in list_traffic_group:

            payload = {
                "name": traffic_group["model"]["name"],
                "failoverMethod": traffic_group["model"]["failover_method"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/cm/traffic-group",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=traffic_group["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="traffic_group",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="traffic_group",
                name_service=traffic_group["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def import_folder(self, list_folder):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for folder in list_folder:

            payload = {
                "name": folder["model"]["name"],
            }

            result = session.post(
                f"https://{self.host}/mgmt/tm/auth/partition/", data=json.dumps(payload)
            )
            self._save_register(
                payload=payload,
                internal_id=folder["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="folder",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="folder",
                name_service=folder["model"]["name"],
                reason=result.text,
            )
            time.sleep(1)
            if result.status_code == 200:
                payload = {
                    "inheritedTrafficGroup": False,
                    "trafficGroup": folder["model"]["traffic_group"],
                }

                result = session.patch(
                    f'https://{self.host}/mgmt/tm/sys/folder/~{folder["model"]["name"]}',
                    data=json.dumps(payload),
                )
                self._save_register(
                    payload=payload,
                    internal_id=folder["model"]["id"],
                    status_code=result.status_code,
                    reason=result.text,
                    service="folder_traffic_group",
                )
                monitor_big.send_status_process_import(
                    status=result.status_code,
                    service="folder_traffic_group",
                    name_service=folder["model"]["name"],
                    reason=result.text,
                )
                time.sleep(0.2)

    # Migração configuração default
    def craeate_default_configuration(self, default):
        self._create_smnp(
            machine_location=default[0]["model"]["snmp_location"],
            snmp_allowed=default[0]["model"]["snmp_allowed"],
            snmp_contact=default[0]["model"]["snmp_contact"],
        )
        self._create_time_zone(
            server=default[0]["model"]["ntp_servers"],
            time_zone=default[0]["model"]["ntp_timezone"],
        )

    def _create_smnp(self, snmp_contact, machine_location, snmp_allowed):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        list_snmp_allowed = snmp_allowed.split(" ")
        payload = {
            "sysContact": snmp_contact,
            "sysLocation": machine_location,
            "allowedAddresses": list_snmp_allowed,
        }
        result = session.patch(
            f"https://{self.host}/mgmt/tm/sys/snmp", data=json.dumps(payload)
        )
        self._save_register(
            payload=payload,
            internal_id="2an23",
            status_code=result.status_code,
            reason=result.text,
            service="smnp",
        )
        monitor_big.send_status_process_import(
            status=result.status_code,
            service="smnp",
            name_service="default",
            reason=result.text,
        )
        time.sleep(0.2)

    def _create_time_zone(self, server, time_zone):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        list_server = server.split(" ")
        payload = {
            "servers": list_server,
            "timezone": time_zone,
        }
        result = session.patch(
            f"https://{self.host}/mgmt/tm/sys/ntp", data=json.dumps(payload)
        )
        self._save_register(
            payload=payload,
            internal_id="2an23",
            status_code=result.status_code,
            reason=result.text,
            service="time_zone",
        )
        monitor_big.send_status_process_import(
            status=result.status_code,
            service="time_zone",
            name_service="default",
            reason=result.text,
        )
        time.sleep(0.2)


class SystemCreateComandsTmsh:
    def __init__(self, external_id):
        self.external_id = external_id

    @staticmethod
    def comands_partition(list_partition):
        list_comands_partition = []

        for partition in list_partition:
            comand = f"create auth partition {partition['model']['name']}"
            list_comands_partition.append(comand)

        return list_comands_partition
