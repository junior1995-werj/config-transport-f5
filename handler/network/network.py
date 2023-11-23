import ast
import json
import time
from datetime import datetime

import requests
from netmiko import ConnectHandler
from sqlalchemy.orm import sessionmaker

from handler.utils.utils import UtilsUtils
from handler.big_ip.models import TansportConfigImportModel
from handler.network.utils import (
    find_vlans,
    find_trunks,
    find_self_ip,
    find_static_routes,
)
from handler.big_ip.monitor import Monitor
from handler.network.models import (
    TrunkModel,
    VlansModel,
    SelfIpModel,
    InterfaceModel,
    StaticRouteModel,
    RoutesDomaninModel,
    PacketFilterRulesModel,
)
from handler.database.connect_db import engine

utils = UtilsUtils()
monitor_big = Monitor()


class Network:
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
        self.comand = NetworkCreateComandsTmsh(external_id=self.external_id)

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

    def create_register_vlans(self):
        sessao = self.session()
        if self.ssh:
            vlans_list = self.net_connect.send_command(
                "list net vlan one-line all-properties"
            )
            vlans_list = find_vlans(vlans_list)

            for vlan in vlans_list:

                vlan_model = VlansModel(**vlan, external_id=self.external_id)
                sessao.add(vlan_model)

        else:
            list_tagged = {
                "0": "False",
                "1": "True",
            }
            root_key = "vlan"
            child_keys_list = [
                "description",
                "id",
                "leaf_name",
                "mac_true",
                "mtu",
                "failsafe_enabled",
                "auto_lasthop",
            ]
            vlans = utils.json_parser(self.file, root_key, child_keys_list)
            root_key = "vlan_member"
            child_keys_list = ["leaf_name", "vmname", "tagged"]
            interfaces = utils.json_parser(self.file, root_key, child_keys_list)

            for vlan in vlans:
                list_interface = []
                vlan["name"] = vlan["leaf_name"]
                del vlan["leaf_name"]
                vlan["tag"] = vlan["id"]
                del vlan["id"]
                vlan["mac"] = vlan["mac_true"]
                del vlan["mac_true"]

                for interface in interfaces:
                    if vlan["name"] == interface["leaf_name"]:
                        list_interface.append(
                            {
                                "name": f"{interface['vmname']}",
                                "untagged": f"{list_tagged[interface['tagged']]}",
                            }
                        )

                vlan["interfaces"] = str(list_interface)
                vlan["comand"] = self.comand.comand_vlan(vlan)
                vlan_model = VlansModel(**vlan, external_id=self.external_id)
                sessao.add(vlan_model)

        sessao.commit()
        sessao.close()

    def get_vlans_by_id(self, external_id):
        sessao = self.session()
        vlans = (
            sessao.query(VlansModel)
            .filter(VlansModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_vlans = []

        for vlan in vlans:
            list_vlans.append(
                {
                    "id": vlan.id,
                    "name": vlan.name,
                    "tag": vlan.tag,
                    "interfaces": vlan.interfaces,
                    "mtu": vlan.mtu,
                    "external_id": vlan.external_id,
                }
            )
        return list_vlans

    def create_register_trunks(self):
        sessao = self.session()
        if self.ssh:
            trunks_list = self.net_connect.send_command("list net trunk one-line")
            trunks_list = find_trunks(trunks_list)

            for trunk in trunks_list:
                trunk_model = TrunkModel(**trunk, external_id=self.external_id)
                sessao.add(trunk_model)
        else:
            list_policy = {
                "0": "auto",
                "1": "  -bandwidth",
            }
            root_key = "trunk"
            child_keys_list = [
                "name",
                "agg_addr",
                "oper_bw",
                "cfg_mbr_count",
                "lacp_enabled",
                "policy",
            ]
            trunks = utils.json_parser(self.file, root_key, child_keys_list)
            root_key = "trunk_cfg_mbr"
            child_keys_list = ["trunk_name", "name"]
            members = utils.json_parser(self.file, root_key, child_keys_list)
            if trunks:
                for trunk in trunks:
                    trunk["bandwidth"] = trunk["oper_bw"]
                    trunk["mac_address"] = trunk["agg_addr"]
                    trunk["link_select_policy"] = list_policy[trunk["policy"]]
                    del trunk["agg_addr"]
                    del trunk["oper_bw"]
                    del trunk["policy"]
                    list_interface = []

                    for member in members:
                        if trunk["name"] == member["trunk_name"]:
                            list_interface.append(member["name"])

                    trunk["interfaces"] = str(list_interface)
                    trunk["comand"] = self.comand.comand_trunk(trunk=trunk)
                    trunk_model = TrunkModel(**trunk, external_id=self.external_id)
                    sessao.add(trunk_model)

        sessao.commit()
        sessao.close()

    def get_trunks_by_id(self, external_id):
        sessao = self.session()
        trumks = (
            sessao.query(TrunkModel)
            .filter(TrunkModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_trumks = []

        for trunk in trumks:
            list_trumks.append(
                {
                    "id": trunk.id,
                    "name": trunk.name,
                    "cfg_mbr_count": trunk.cfg_mbr_count,
                    "bandwidth": trunk.bandwidth,
                    "interfaces": trunk.interfaces,
                    "link_select_policy": trunk.link_select_policy,
                    "mac_address": trunk.mac_address,
                    "lacp_enabled": trunk.lacp_enabled,
                    "external_id": trunk.external_id,
                }
            )
        return list_trumks

    def create_register_static_route(self):
        sessao = self.session()
        if self.ssh:
            static_route_list = self.net_connect.send_command("list net route one-line")
            static_route_list = find_static_routes(static_route_list)

            for static_route in static_route_list:
                static_route_model = StaticRouteModel(
                    **static_route, external_id=self.external_id
                )
                sessao.add(static_route_model)
        else:
            root_key = "route_static_entry"
            child_keys_list = [
                "leaf_name",
                "dest",
                "netmask",
                "gateway",
                "partition_id",
            ]
            route_static_entry = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "route_mgmt_entry"
            child_keys_list = ["leaf_name", "dest", "netmask", "gateway"]
            route_mgmt_entry = utils.json_parser(self.file, root_key, child_keys_list)

            if route_static_entry:
                if route_mgmt_entry:
                    route_static_entry.extend(route_mgmt_entry)
                for route in route_static_entry:
                    route["name"] = route["leaf_name"]
                    route["destination"] = route["dest"]
                    del route["leaf_name"]
                    del route["dest"]

                    route["comand"] = self.comand.comand_static_route(
                        static_route=route
                    )
                    route_model = StaticRouteModel(
                        **route, external_id=self.external_id
                    )
                    sessao.add(route_model)
        sessao.commit()
        sessao.close()

    def get_static_route_by_id(self, external_id):
        sessao = self.session()
        static_routes = (
            sessao.query(StaticRouteModel)
            .filter(StaticRouteModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_static_routes = []

        for static_route in static_routes:
            list_static_routes.append(
                {
                    "id": static_route.id,
                    "name": static_route.name,
                    "destination": static_route.destination,
                    "netmask": static_route.netmask,
                    "gateway": static_route.gateway,
                    "external_id": static_route.external_id,
                }
            )
        return list_static_routes

    def create_register_self_ip(self):
        sessao = self.session()
        if self.ssh:
            self_ip_list = self.net_connect.send_command("list net self one-line")
            self_ip_list = find_self_ip(self_ip_list)

            for static_route in self_ip_list:
                static_route_model = SelfIpModel(
                    **static_route, external_id=self.external_id
                )
                sessao.add(static_route_model)
        else:
            self_port_protocol = {
                "0": "all",
                "1": "icmp",
                "2": "igmp",
                "6": "tcp",
                "17": "udp",
                "89": "ospf",
                "256": "all",  # validar
            }
            root_key = "self_ip"
            child_keys_list = [
                "leaf_name",
                "addr",
                "netmask",
                "vlan_name",
                "traffic_group",
                "partition_id",
            ]
            self_ips = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "self_port"
            child_keys_list = ["self_name", "protocol", "port", "leaf_name"]
            self_ports = utils.json_parser(self.file, root_key, child_keys_list)
            if self_ips:
                for self_ip in self_ips:
                    self_ip["name"] = self_ip["leaf_name"]
                    self_ip["vlan"] = self_ip["vlan_name"]
                    self_ip["ip_addr"] = self_ip["addr"]
                    del self_ip["leaf_name"]
                    del self_ip["vlan_name"]
                    del self_ip["addr"]
                    list_self_port = []
                    if self_ports:
                        for self_port in self_ports:
                            if self_port["leaf_name"] == self_ip["name"]:
                                list_self_port.append(
                                    {
                                        "protocol": f"{self_port_protocol[self_port['protocol']]}"
                                    }
                                )

                    self_ip["port_lock_down"] = str(list_self_port)
                    self_ip["comand"] = self.comand.comand_self_ip(self_ip=self_ip)
                    vlan_model = SelfIpModel(**self_ip, external_id=self.external_id)
                    sessao.add(vlan_model)

        sessao.commit()
        sessao.close()

    def get_self_ip_by_id(self, external_id):
        sessao = self.session()
        self_ips = (
            sessao.query(SelfIpModel)
            .filter(SelfIpModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_self_ips = []

        for self_ip in self_ips:
            list_self_ips.append(
                {
                    "id": self_ip.id,
                    "name": self_ip.name,
                    "ip_addr": self_ip.ip_addr,
                    "net_mask": self_ip.net_mask,
                    "vlan": self_ip.vlan,
                    "port_lock_down": self_ip.port_lock_down,
                    "traffic_group": self_ip.traffic_group,
                    "external_id": self_ip.external_id,
                }
            )
        return list_self_ips

    def create_register_interface(self):
        sessao = self.session()
        if self.ssh:
            pass
            # implementar
        else:
            root_key = "interface"
            child_keys_list = [
                "name",
                "vendor_name",
                "vendor_partnum",
                "serial_number",
                "mac_addr",
                "mtu",
            ]
            interfaces = utils.json_parser(self.file, root_key, child_keys_list)
            if interfaces:
                for interface in interfaces:
                    interface_model = InterfaceModel(
                        **interface, external_id=self.external_id
                    )
                    sessao.add(interface_model)

        sessao.commit()
        sessao.close()

    def get_interface_by_id(self, external_id):
        sessao = self.session()
        interfaces = (
            sessao.query(InterfaceModel)
            .filter(InterfaceModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_interfaces = []

        for interface in interfaces:
            list_interfaces.append(
                {
                    "id": interface.id,
                    "name": interface.name,
                    "vendor_name": interface.vendor_name,
                    "vendor_partnum": interface.vendor_partnum,
                    "serial_number": interface.serial_number,
                    "mac_addr": interface.mac_addr,
                    "mtu": interface.mtu,
                    "external_id": interface.external_id,
                }
            )
        return list_interfaces

    def create_register_routes_domains(self):
        sessao = self.session()

        root_key = "route_domain"
        child_keys_list = ["id", "leaf_name", "strict", "conn_limit", "partition_id"]
        route_domains = utils.json_parser(self.file, root_key, child_keys_list)
        root_key = "route_domain_vlan"
        child_keys_list = ["vlan_name", "leaf_name"]
        route_domain_vlans = utils.json_parser(self.file, root_key, child_keys_list)
        root_key = "route_domain_routing_protocol"
        child_keys_list = ["protocol_name", "domain_name"]
        route_domain_routing_protocols = utils.json_parser(
            self.file, root_key, child_keys_list
        )

        root_key = "auth_partition"
        child_keys_list = ["name", "default_rd_id"]
        route_domain_default = utils.json_parser(self.file, root_key, child_keys_list)

        for route_domain in route_domains:
            route_domain["name"] = route_domain["leaf_name"]
            del route_domain["leaf_name"]
            route_domain["strick_isolation"] = route_domain["strict"]
            del route_domain["strict"]
            route_domain["id_route"] = route_domain["id"]
            del route_domain["id"]

            list_vlans = []

            for vlan in route_domain_vlans:
                if vlan["leaf_name"] == route_domain["name"]:
                    list_vlans.append(vlan["vlan_name"])

            route_domain["vlans"] = str(list_vlans)

            list_routing_protocol = []
            for routing_protocol in route_domain_routing_protocols:
                name = routing_protocol["domain_name"].split("/")
                name = name[2]
                if name == route_domain["name"]:
                    list_routing_protocol.append(routing_protocol["protocol_name"])
            route_domain["dynamic_routing_protocols"] = str(list_routing_protocol)

            for default in route_domain_default:
                if (
                    route_domain["partition_id"] == default["name"]
                    and route_domain["id_route"] == default["default_rd_id"]
                ):
                    route_domain["route_default"] = True
                    break
                else:
                    route_domain["route_default"] = False

            route_domain["comand"] = self.comand.comand_route_domain(
                route_domain=route_domain
            )

            sessao.add(RoutesDomaninModel(**route_domain, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_routes_domains_by_id(self, external_id):
        sessao = self.session()
        routes_domains = (
            sessao.query(RoutesDomaninModel)
            .filter(RoutesDomaninModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_routes_domain = []

        for routes_domain in routes_domains:
            list_routes_domain.append(
                {
                    "id": routes_domain.id,
                    "id_route": routes_domain.id_route,
                    "name": routes_domain.name,
                    "strick_isolation": routes_domain.strick_isolation,
                    "vlans": routes_domain.vlans,
                    "dynamic_routing_protocols": routes_domain.dynamic_routing_protocols,
                    "conn_limit": routes_domain.conn_limit,
                    "partition_id": routes_domain.partition_id,
                    "external_id": routes_domain.external_id,
                }
            )
        return list_routes_domain

    def create_register_packet_filters_rule(self):
        sessao = self.session()

        dict_actions = {
            "1": "Accept",
            "2": "Discard",
            "3": "Reject",
            "4": "Continue",
        }
        dict_log = {
            "0": "Disabled",
            "1": "Enabled",
        }
        dict_order = {
            "5": "First",
            "10": "Last",
        }
        root_key = "packet_filter_rule"
        child_keys_list = [
            "leaf_name",
            "expression",
            "action",
            "vname",
            "order_weight",
            "log",
            "folder_name",
            "partiton_id",
        ]
        packet_filter_rules = utils.json_parser(self.file, root_key, child_keys_list)

        for packet_filter_rule in packet_filter_rules:
            packet_filter_rule["name"] = packet_filter_rule["leaf_name"]
            del packet_filter_rule["leaf_name"]
            packet_filter_rule["action"] = dict_actions[packet_filter_rule["action"]]
            packet_filter_rule["order_weight"] = dict_order[
                packet_filter_rule["order_weight"]
            ]
            packet_filter_rule["log"] = dict_log[packet_filter_rule["log"]]
            packet_filter_rule["comand"] = ""
            sessao.add(
                PacketFilterRulesModel(
                    **packet_filter_rule, external_id=self.external_id
                )
            )

        sessao.commit()
        sessao.close()

    def get_packet_filters_rule_by_id(self, external_id):
        sessao = self.session()
        packet_filter_rules = (
            sessao.query(PacketFilterRulesModel)
            .filter(PacketFilterRulesModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_packet_filter_rules = []

        for packet_filter_rule in packet_filter_rules:
            list_packet_filter_rules.append(
                {
                    "id": packet_filter_rule.id,
                    "name": packet_filter_rule.name,
                    "expression": packet_filter_rule.expression,
                    "action": packet_filter_rule.action,
                    "vname": packet_filter_rule.vname,
                    "order_weight": packet_filter_rule.order_weight,
                    "log": packet_filter_rule.log,
                    "partiton_id": packet_filter_rule.partiton_id,
                    "external_id": packet_filter_rule.external_id,
                }
            )
        return list_packet_filter_rules


class NetworkMigrate:
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

    def create_vlan(self, list_vlan):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for vlan in list_vlan:
            payload = {
                "name": vlan["model"]["name"],
                "mtu": vlan["model"]["mtu"],
                "failsafe": dict_enable[vlan["model"]["failsafe_enabled"]],
                "auto_lasthop": dict_enable[vlan["model"]["auto_lasthop"]],
                "description": vlan["model"]["description"],
                "interfacesReference": ast.literal_eval(vlan["model"]["interfaces"]),
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/net/vlan", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=vlan["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="vlan",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="vlan",
                name_service=vlan["model"]["name"],
                reason=result.text,
            )

            time.sleep(0.2)

    def create_trunks(self, list_trunks):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for trumk in list_trunks:
            payload = {
                "name": trumk["model"]["name"],
                "cfgMbrCount": trumk["model"]["cfg_mbr_count"],
                "bandwidth": trumk["model"]["bandwidth"],
                "interfaces": ast.literal_eval(trumk["model"]["interfaces"]),
                "linkSelectPolicy": trumk["model"]["link_select_policy"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/net/trunk", data=json.dumps(payload)
            )
            self._save_register(
                payload=payload,
                internal_id=trumk["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="trumk",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="trumk",
                name_service=trumk["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    @staticmethod
    def get_self_ip_from_traffic_group(self_ips, init=True):
        list_return = []
        if init:
            for self_ip in self_ips:
                if (
                    self_ip["model"]["traffic_group"]
                    == "/Common/traffic-group-local-only"
                ):
                    list_return.append(self_ip)
        else:
            for self_ip in self_ips:
                if (
                    self_ip["model"]["traffic_group"]
                    != "/Common/traffic-group-local-only"
                ):
                    list_return.append(self_ip)

        return list_return

    def create_self_ip(self, list_self_ip: list):

        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        list_self_ip_order = self.get_self_ip_from_traffic_group(list_self_ip)
        list_self_ip_order.extend(
            self.get_self_ip_from_traffic_group(list_self_ip, init=False)
        )

        for self_ip in list_self_ip_order:
            port_lock_down = ast.literal_eval(self_ip["model"]["port_lock_down"])
            payload = {
                "name": self_ip["model"]["name"],
                "address": f"{self_ip['model']['ip_addr']}/{utils.calculator_mask(self_ip['model']['net_mask'])}",
                "vlan": self_ip["model"]["vlan"],
                "trafficGroup": self_ip["model"]["traffic_group"],
                "allowService": []
                if port_lock_down == []
                else port_lock_down[0]["protocol"],
                "partition": self_ip["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/net/self", data=json.dumps(payload)
            )
            self._save_register(
                payload=payload,
                internal_id=self_ip["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="self_ip",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="self_ip",
                name_service=self_ip["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_static_route(self, list_static_route):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for static_route in list_static_route:
            payload = {
                "name": static_route["model"]["name"],
                "gw": static_route["model"]["gateway"],
                "network": f"{static_route['model']['destination']}/{utils.calculator_mask(static_route['model']['netmask'])}",
                "partition": static_route["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/net/route", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=static_route["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="static_route",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="static_route",
                name_service=static_route["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_route_domain(self, list_route_domain):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for route_domain in list_route_domain:
            payload = {
                "name": route_domain["model"]["name"],
                "id": route_domain["model"]["id_route"],
                "vlans": ast.literal_eval(route_domain["model"]["vlans"]),
                "partition": route_domain["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/net/route-domain",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=route_domain["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="route_domain",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="route_domain",
                name_service=route_domain["model"]["name"],
                reason=result.text,
            )

            if result.status_code == 200 and route_domain["model"]["route_default"]:
                payload = {
                    "defaultRouteDomain": route_domain["model"]["id_route"],
                }

                result = session.patch(
                    f'https://{self.host}/mgmt/tm/auth/partition/{route_domain["model"]["partition_id"]}/',
                    data=json.dumps(payload),
                )
                self._save_register(
                    payload=payload,
                    internal_id=route_domain["model"]["id"],
                    status_code=result.status_code,
                    reason=result.text,
                    service="route_domain_update_partition",
                )
                monitor_big.send_status_process_import(
                    status=result.status_code,
                    service="route_domain_update_partition",
                    name_service=route_domain["model"]["name"],
                    reason=result.text,
                )
            time.sleep(0.2)


class NetworkCreateComandsTmsh:
    def __init__(self, external_id):
        self.external_id = external_id

    @staticmethod
    def comand_route_domain(route_domain):
        comand = f"create net route-domain /{route_domain['partition_id']}/{route_domain['name']} id {route_domain['id_route']} "

        if ast.literal_eval(route_domain["vlans"]) != []:
            vlans = "vlans add {"
            for vlan in ast.literal_eval(route_domain["vlans"]):
                vlans += " " + vlan + " "
            vlans += "}"
            comand += vlans
        return comand

    @staticmethod
    def comand_vlan(vlan):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }

        comand = f"create net vlan {vlan['name']} mtu {vlan['mtu']} "
        if ast.literal_eval(vlan["interfaces"]) != []:
            interface = "interfaces add {"
            for valor in ast.literal_eval(vlan["interfaces"]):
                interface += " " + valor["name"] + " "
            interface += "}"
            comand += interface

        comand += f" failsafe {dict_enable[vlan['failsafe_enabled']]} auto-lasthop {dict_enable[vlan['auto_lasthop']]} description {vlan['description']}"

        return comand

    @staticmethod
    def comand_self_ip(self_ip):
        comand = f"create net self /{self_ip['partition_id']}/{self_ip['name']} address {self_ip['ip_addr']}/{utils.calculator_mask(self_ip['netmask'])} "
        comand += f"vlan {self_ip['vlan']} traffic-group {self_ip['traffic_group']}"

        if ast.literal_eval(self_ip["port_lock_down"]) != []:
            allow = (
                "allow-service add {"
                + ast.literal_eval(self_ip["port_lock_down"])[0]["protocol"]
                + " }"
            )
            comand += allow

        return comand

    @staticmethod
    def comand_trunk(trunk):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }

        comand = f"create net trunk {trunk['name']} lacp {dict_enable[trunk['lacp_enabled']]} "

        if ast.literal_eval(trunk["interfaces"]) != []:
            interface = "interfaces add {"
            for inter in ast.literal_eval(trunk["interfaces"]):
                interface += " " + inter + " "
            comand += interface + "}"

        return comand

    @staticmethod
    def comand_static_route(static_route: dict):
        if "partition_id" not in static_route.keys():
            static_route["partition_id"] = "Common"
        comand = f"create net route /{static_route['partition_id']}/{static_route['name']} gw {static_route['gateway']} "
        comand += f"network {static_route['destination']}/{utils.calculator_mask(static_route['netmask'])}"

        return comand
