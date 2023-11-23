import ast
import json
import time
from datetime import datetime

import requests
from netmiko import ConnectHandler
from sqlalchemy.orm import sessionmaker

from handler.utils.utils import UtilsUtils
from handler.big_ip.models import TansportConfigImportModel
from handler.big_ip.monitor import Monitor
from handler.database.connect_db import engine
from handler.ltm.generic_message.models import (
    PeerModel,
    RouteModel,
    RouterModel,
    ProtocolModel,
    GmTransportConfigModel,
)

utils = UtilsUtils()
monitor_big = Monitor()


class GenenricMessage:
    def __init__(
        self, external_id=None, host=None, username=None, password=None, file=None
    ):
        self._host = host
        self._username = username
        self._password = password
        self.net_connect = None
        self.external_id = external_id
        self.ssh = False
        self.file = file
        if self._username and self._password and self._host and self.external_id:
            self.connect()
        self.session = sessionmaker(bind=engine)
        self.comands = GenericMessageCreateComandsTmsh(external_id=self.external_id)

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

    def create_register_peer(self):
        sessao = self.session()
        root_key = "message_routing_peer"
        child_keys_list = [
            "leaf_name",
            "pool",
            "auto_initialization",
            "transport_name",
            "partition_id",
        ]
        peers = utils.json_parser(self.file, root_key, child_keys_list)

        for peer in peers:
            peer["name"] = peer["leaf_name"]
            del peer["leaf_name"]
            peer["comand"] = self.comands.comands_peer(peer=peer)
            sessao.add(PeerModel(**peer, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_peer_by_id(self, external_id):
        sessao = self.session()
        peers = (
            sessao.query(PeerModel)
            .filter(PeerModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_peers = []

        for peer in peers:
            list_peers.append(
                {
                    "id": peer.id,
                    "name": peer.name,
                    "pool": peer.pool,
                    "transport_name": peer.transport_name,
                    "auto_initialization": peer.auto_initialization,
                    "external_id": peer.external_id,
                }
            )
        return list_peers

    def create_register_protocol(self):

        sessao = self.session()
        root_key = "profile_genericmsg"
        child_keys_list = ["leaf_name", "disable_parser", "partition_id"]
        protocols = utils.json_parser(self.file, root_key, child_keys_list)

        for protocol in protocols:
            if protocol["leaf_name"] not in ["genericmsg"]:
                protocol["name"] = protocol["leaf_name"]
                del protocol["leaf_name"]
                protocol["comand"] = self.comands.comands_protocol(protocol=protocol)
                sessao.add(ProtocolModel(**protocol, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_protocol_by_id(self, external_id):
        sessao = self.session()
        protocols = (
            sessao.query(ProtocolModel)
            .filter(ProtocolModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_protocols = []

        for peer in protocols:
            list_protocols.append(
                {
                    "id": peer.id,
                    "name": peer.name,
                    "disable_parser": peer.disable_parser,
                    "external_id": peer.external_id,
                }
            )
        return list_protocols

    def create_register_route(self):

        sessao = self.session()
        root_key = "genericmsg_route"
        child_keys_list = ["leaf_name", "partition_id"]
        routes = utils.json_parser(self.file, root_key, child_keys_list)

        root_key = "genericmsg_route_message_routing_peer"
        child_keys_list = ["leaf_name", "message_routing_peer_name"]
        peers = utils.json_parser(self.file, root_key, child_keys_list)

        for route in routes:
            list_peers = []
            route["name"] = route["leaf_name"]
            del route["leaf_name"]
            for peer in peers:
                if peer["leaf_name"] == route["name"]:
                    list_peers.append(peer["message_routing_peer_name"])
            route["peer"] = str(list_peers)
            route["comand"] = self.comands.comands_route(route=route)
            sessao.add(RouteModel(**route, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_route_by_id(self, external_id):
        sessao = self.session()
        routes = (
            sessao.query(RouteModel)
            .filter(RouteModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_routes = []

        for route in routes:
            list_routes.append(
                {
                    "id": route.id,
                    "name": route.name,
                    "peer": route.peer,
                    "external_id": route.external_id,
                }
            )
        return list_routes

    def create_register_router(self):

        sessao = self.session()
        root_key = "messagerouter_genericmsg_route"
        child_keys_list = ["leaf_name", "genericmsg_route_name", "partition_id"]
        routers = utils.json_parser(self.file, root_key, child_keys_list)

        for router in routers:
            router["comand"] = self.comands.comands_router(router=router)
            sessao.add(
                RouterModel(
                    name=router["leaf_name"],
                    route=router["genericmsg_route_name"],
                    partition_id=router["partition_id"],
                    comand=router["comand"],
                    external_id=self.external_id,
                ),
            )
        sessao.commit()
        sessao.close()

    def get_router_by_id(self, external_id):
        sessao = self.session()
        routers = (
            sessao.query(RouterModel)
            .filter(RouterModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_routers = []

        for router in routers:
            list_routers.append(
                {
                    "id": router.id,
                    "name": router.name,
                    "route": router.route,
                    "external_id": router.external_id,
                }
            )
        return list_routers

    def create_register_transport_config(self):
        sessao = self.session()
        root_key = "transport_config"
        child_keys_list = ["leaf_name", "partition_id"]
        transport_configs = utils.json_parser(self.file, root_key, child_keys_list)

        root_key = "transport_config_profile"
        child_keys_list = ["leaf_name", "profile_name"]
        transport_config_profiles = utils.json_parser(
            self.file, root_key, child_keys_list
        )

        root_key = "transport_config_rule"
        child_keys_list = ["leaf_name", "rule_name"]
        transport_config_rules = utils.json_parser(self.file, root_key, child_keys_list)

        for transport_config in transport_configs:
            list_profiles = []
            list_rules = []
            transport_config["name"] = transport_config["leaf_name"]
            del transport_config["leaf_name"]

            for profile in transport_config_profiles:
                if profile["leaf_name"] == transport_config["name"]:
                    list_profiles.append({"name": profile["profile_name"]})
            transport_config["profiles"] = str(list_profiles)

            for rule in transport_config_rules:
                if rule["leaf_name"] == transport_config["name"]:
                    list_rules.append(rule["rule_name"])

            transport_config["rule"] = str(list_rules)
            transport_config["comand"] = self.comands.comands_transport_config(
                transport_config=transport_config
            )
            sessao.add(
                GmTransportConfigModel(**transport_config, external_id=self.external_id)
            )
        sessao.commit()
        sessao.close()

    def get_transport_config_by_id(self, external_id):
        sessao = self.session()
        transport_configs = (
            sessao.query(GmTransportConfigModel)
            .filter(GmTransportConfigModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_transport_configs = []

        for transport_config in transport_configs:
            list_transport_configs.append(
                {
                    "id": transport_config.id,
                    "name": transport_config.name,
                    "rule": transport_config.rule,
                    "profiles": transport_config.profiles,
                    "external_id": transport_config.external_id,
                }
            )
        return list_transport_configs


class GenenricMessageMigrate:
    def __init__(self, host, username, password, external_id, user_migrate):
        self.host = host
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

    def create_peer(self, list_peer):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for peer in list_peer:
            payload = {
                "name": peer["model"]["name"],
                "pool": peer["model"]["pool"],
                "transportConfig": peer["model"]["transport_name"],
                "autoInitialization": dict_enable[peer["model"]["auto_initialization"]],
                "partition": peer["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/message-routing/generic/peer",
                data=json.dumps(payload),
            )
            self._save_register(
                payload=payload,
                internal_id=peer["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="peer",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="peer",
                name_service=peer["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_protocol(self, list_protocol):
        dict_enable = {
            "0": "no",
            "1": "yes",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for protocol in list_protocol:
            payload = {
                "name": protocol["model"]["name"],
                "disableParser": dict_enable[protocol["model"]["disable_parser"]],
                "partition": protocol["model"]["partition_id"],
            }

            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/message-routing/generic/protocol",
                data=json.dumps(payload),
            )
            self._save_register(
                payload=payload,
                internal_id=protocol["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="protocol",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="protocol",
                name_service=protocol["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_route(self, list_route):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for route in list_route:
            payload = {
                "name": route["model"]["name"],
                "peers": ast.literal_eval(route["model"]["peer"]),
                "partition": route["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/message-routing/generic/route",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=route["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="route",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="route",
                name_service=route["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_router(self, list_router):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for router in list_router:
            payload = {
                "name": router["model"]["name"],
                "routes": [router["model"]["route"]],
                "partition": router["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/message-routing/generic/router",
                data=json.dumps(payload),
            )
            self._save_register(
                payload=payload,
                internal_id=router["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="router",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="router",
                name_service=router["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_gm_transport_config(self, list_transport_config):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for tc in list_transport_config:
            payload = {
                "name": tc["model"]["name"],
                "rules": ast.literal_eval(tc["model"]["rule"]),
                "profiles": ast.literal_eval(tc["model"]["profiles"]),
                "partition": tc["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/message-routing/generic/transport-config",
                data=json.dumps(payload),
            )
            self._save_register(
                payload=payload,
                internal_id=tc["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="transport_config",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="transport_config",
                name_service=tc["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)


class GenericMessageCreateComandsTmsh:
    def __init__(self, external_id):
        self.external_id = external_id

    @staticmethod
    def comands_peer(peer):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }
        comand = f" create ltm message-routing generic peer /{peer['partition_id']}/{peer['name']} pool {peer['pool']}"
        comand += f" transport-config {peer['transport_name']} auto-initialization {dict_enable[peer['auto_initialization']]}"
        return comand

    @staticmethod
    def comands_protocol(protocol):
        dict_enable = {
            "0": "no",
            "1": "yes",
        }
        comand = f"create ltm message-routing generic protocol /{protocol['partition_id']}/{protocol['name']} disable-parser {dict_enable[protocol['disable_parser']]}"
        return comand

    @staticmethod
    def comands_route(route):
        comand = (
            f"create ltm message-routing generic route /{route['partition_id']}/{route['name']} peers"
            + "{"
            + f" {ast.literal_eval(route['peer'])[0]}"
            + " }"
        )
        return comand

    @staticmethod
    def comands_router(router):
        comand = (
            f"create ltm message-routing generic router /{router['partition_id']}/{router['leaf_name']} routes add "
            + "{ "
            + router["genericmsg_route_name"]
            + " }"
        )
        return comand

    @staticmethod
    def comands_transport_config(transport_config):
        comand = f"create ltm message-routing generic transport-config /{transport_config['partition_id']}/{transport_config['name']}"
        comand += " rules { " + ast.literal_eval(transport_config["rule"])[0] + " }"
        if ast.literal_eval(transport_config["profiles"]):
            comand += " profiles add {"
            for profile in ast.literal_eval(transport_config["profiles"]):
                comand += " " + profile["name"] + " "
            comand += "}"
        return comand
