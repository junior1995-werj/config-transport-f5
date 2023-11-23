import ast
import json
import time
from datetime import datetime

import requests
from netmiko import ConnectHandler
from sqlalchemy.orm import sessionmaker

from handler.ltm.models import (
    NatModel,
    PoolModel,
    SnatModel,
    MonitorModel,
    PoliciesModel,
    SnatpoolModel,
    DataGroupModel,
    ProfilesSSLModel,
    ProfilesOtherModel,
    VirtualServersModel,
    ProfilesPersistModel,
    ProfilesProtocolModel,
    ProfilesServicesModel,
    iRuleModel,
)
from handler.utils.utils import LtmUtils, UtilsUtils
from handler.big_ip.models import TansportConfigImportModel
from handler.big_ip.monitor import Monitor
from handler.ltm.collections import (
    PROFILES_OTHERS,
    LIST_PROFILE_TYPES,
    PROFILES_OTHERS_API,
    PROFILES_SSL_IGNORE,
    PROFILES_OTHER_IGNORE,
    LIST_PROFILE_PROTO_TYPE,
    PROFILES_PERSIST_IGNORE,
    PROFILES_PROTOCOL_IGNORE,
    PROFILES_SERVICES_IGNORE,
)
from handler.database.connect_db import engine

ltm_utils = LtmUtils()
utils = UtilsUtils()
monitor_big = Monitor()


class Ltm:
    def __init__(
        self, external_id=None, host=None, username=None, password=None, file=None
    ):
        self._host = host
        self._username = username
        self._password = password
        self.net_connect = None
        self.external_id = external_id
        self.file = file
        self.ssh = False
        if self._username and self._password and self._host and self.external_id:
            self.connect()
        self.session = sessionmaker(bind=engine)
        self.comands = LtmCreateComandsTmsh(external_id=self.external_id)

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

    def create_register_database_pool_and_members(self):

        sessao = self.session()
        if self.ssh:
            pool_list = self.net_connect.send_command("list ltm pool |grep ltm")
            pool_list = ltm_utils.find_pool_name_tmsh(pool_list)

            for pool in pool_list:

                members = self.net_connect.send_command(
                    f"list ltm pool {pool} members | grep -E ':'"
                )
                load_balance_mode = self.net_connect.send_command(
                    f"list ltm pool {pool} load-balancing-mode | grep mode"
                )
                monitor = self.net_connect.send_command(
                    f"list ltm pool {pool} monitor | grep monitor"
                )
                members, load_balance_mode, monitor = ltm_utils.get_propert_pool(
                    members, load_balance_mode, monitor
                )

                list_members = []
                for member in members:
                    list_members.append(member)

                pool_model = PoolModel(
                    name=pool,
                    members=list_members,
                    loadBalancingMode=load_balance_mode,
                    monitor=monitor,
                    external_id=self.external_id,
                )
                sessao.add(pool_model)
        else:
            dict_lb_method = {
                "0": "0 - Round Robin",
                "1": "1 - Ratio (member)",
                "2": "2 - Least Connections (member)",
                "3": "3 - Observed (member)",
                "4": "4 - Predictive (member)",
                "5": "5 - Ratio (node)",
                "6": "6 - Least Connections (node)",
                "7": "7 - Fastest (node)",
                "8": "8 - Observed (node)",
                "9": "9 - Predictive (node)",
                "10": "10 - Dynamic Ratio (node)",
                "11": "11 - Fastest (application)",
                "12": "12 - Least Sessions",
                "13": "13 - Dynamic Ratio (member)",
                "15": "15 - Weighted Least Connections (member)",
                "16": "16 - Weighted Least Connections (node)",
                "17": "17 - Ratio (session)",
                "18": "18 - Ratio Least Connections (member)",
                "19": "19 - Ratio Least Connections (node)",
            }
            root_key = "pool"
            child_keys_list = [
                "description",
                "leaf_name",
                "lb_mode",
                "monitor_rule",
                "partition_id",
            ]
            pools = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "pool_member"
            child_keys_list = ["addr", "port", "leaf_name", "monitor_rule"]
            pool_members = utils.json_parser(self.file, root_key, child_keys_list)

            for pool in pools:
                pool["name"] = pool["leaf_name"]
                pool["loadBalancingMode"] = dict_lb_method[pool["lb_mode"]]
                pool["monitor"] = pool["monitor_rule"]
                del pool["leaf_name"]
                del pool["lb_mode"]
                del pool["monitor_rule"]
                list_members = []
                for pool_member in pool_members:
                    if pool_member["leaf_name"] == pool["name"]:
                        list_members.append(
                            {
                                "name": f"{pool_member['addr']}:{pool_member['port']}",
                                "monitor": pool_member["monitor_rule"],
                            }
                        )
                pool["members"] = str(list_members)
                pool["comand"] = self.comands.comands_pools(pool=pool)
                sessao.add(PoolModel(**pool, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_virtual_server(self):
        sessao = self.session()
        if self.ssh:
            vs_list = self.net_connect.send_command("list ltm virtual | grep ltm")
            vs_list = ltm_utils.find_vs_tmsh(vs_list)

            for vs in vs_list:
                destination = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep destination"
                )
                mask = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep mask"
                )
                source = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep source"
                )
                ip_protocol = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep ip-protocol"
                )

                sourceAddressTranslation = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep type"
                )
                translateAddress = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep translate-a "
                )
                translatePort = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep translate-p "
                )

                string = f"list ltm virtual {vs} profiles | grep"
                profiles = self.net_connect.send_command(string + "{")

                rulesReference = self.net_connect.send_command(
                    f"list ltm virtual {vs} rules"
                )
                pool = self.net_connect.send_command(
                    f"list ltm virtual {vs} | grep pool"
                )
                policies = self.net_connect.send_command(
                    f"list ltm virtual {vs} policies | grep policies"
                )

                dict_return = ltm_utils.get_prop_vs(
                    destination=destination,
                    mask=mask,
                    ipProtocol=ip_protocol,
                    pool=pool,
                    profilesReference=profiles,
                    translateAddress=translateAddress,
                    translatePort=translatePort,
                    sourceAddressTranslation=sourceAddressTranslation,
                    source=source,
                    rulesReference=rulesReference,
                    policies=policies,
                )

                virtual_server_model = VirtualServersModel(
                    name=vs, **dict_return, external_id=self.external_id
                )
                sessao.add(virtual_server_model)

        else:
            dict_ip_proto = {
                "0": "1 - * All Protocols",
                "6": "6 - TCP",
                "17": "17 - UDP",
                "132": "132 - SCTP",
                "50": "50 - IPsec ESP",
                "51": "51 - IPsec AH",
            }
            dict_sour_add_trans = {
                "1": "1 - SNAT",
                "3": "3 - Auto Map",
                "0": "0 - None",
            }
            dict_type = {
                "0": "Standard",
                "2": "Forwarding (Layer 2)",
                "1": "Forwarding (IP)",
                "7": "DHCP",
                "4": "Performance (Layer 4)",
                "5": "Performance (HTTP)",
                "6": "Stateless",
                "3": "Reject",
                "8": "Internal",
                "9": "Message Routing",
            }
            root_key = "virtual_server"
            child_keys_list = [
                "leaf_name",
                "description",
                "type",
                "addr",
                "port",
                "wildmask",
                "src_addr",
                "ip_proto",
                "source_address_translation_type",
                "translate_addr",
                "translate_port",
                "default_pool",
                "partition_id",
            ]
            virtual_servers = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "virtual_server_profile"
            child_keys_list = ["leaf_name", "profile_name"]
            virtual_server_profiles = utils.json_parser(
                self.file, root_key, child_keys_list
            )

            root_key = "virtual_server_rule"
            child_keys_list = ["leaf_name", "rule_name"]
            virtual_server_rules = utils.json_parser(
                self.file, root_key, child_keys_list
            )

            for virtual in virtual_servers:
                virtual["name"] = virtual["leaf_name"]
                virtual["destination"] = virtual["addr"]
                virtual["type"] = dict_type[virtual["type"]]
                virtual["mask"] = virtual["wildmask"]
                virtual["source"] = virtual["src_addr"]
                virtual["ip_proto"] = dict_ip_proto[virtual["ip_proto"]]
                virtual["source_address_translation_type"] = dict_sour_add_trans[
                    virtual["source_address_translation_type"]
                ]
                virtual["pool"] = virtual["default_pool"]
                if virtual["pool"] is not None:
                    virtual["pool"] = virtual["pool"].replace("/Common/", "")
                del virtual["leaf_name"]
                del virtual["addr"]
                del virtual["wildmask"]
                del virtual["src_addr"]
                del virtual["default_pool"]

                list_profiles = []
                for profile in virtual_server_profiles:
                    if profile["leaf_name"] == virtual["name"]:
                        list_profiles.append(
                            profile["profile_name"].replace("/Common/", "")
                        )
                virtual["profilesReference"] = str(list_profiles)

                list_rules = []
                for rule in virtual_server_rules:
                    if rule["leaf_name"] == virtual["name"]:
                        list_rules.append(rule["rule_name"].replace("/Common/", ""))

                virtual["rulesReference"] = str(list_rules)
                virtual["comand"] = self.comands.comands_virtual_server(vs=virtual)
                sessao.add(VirtualServersModel(**virtual, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_irule_and_datagroups(self):
        sessao = self.session()
        if self.ssh:
            datagroups_list = rules_list = self.net_connect.send_command(
                "list ltm data-group internal one-line"
            )
            datagroups_list = ltm_utils.find_and_get_prop_datagroup(datagroups_list)

            for datagroup in datagroups_list:
                datagroup_model = DataGroupModel(
                    **datagroup, external_id=self.external_id
                )

                sessao.add(datagroup_model)

            sessao.commit()

            rules_list = self.net_connect.send_command(
                "list ltm rule non-default-properties recursive | grep rule | grep -v _sys_ | grep -v '#'"
            )
            irules_list = ltm_utils.find_rule(rules_list)

            for irule in irules_list:
                rule = self.net_connect.send_command(f"list ltm rule {irule}")
                rule = ltm_utils.get_irule(rule)
                irule_model = iRuleModel(
                    name=irule, apiAnonymous=rule, external_id=self.external_id
                )

                sessao.add(irule_model)
        else:
            # datagroup
            list_type_data = {
                "1": "ip",
                "2": "string",
                "3": "integer",  # validar
            }
            root_key = "value_list"
            child_keys_list = ["leaf_name", "type", "partition_id"]
            datagroups = utils.json_parser(self.file, root_key, child_keys_list)
            root_key = "class_string_item"
            child_keys_list = ["leaf_name", "value", "data"]
            values = utils.json_parser(self.file, root_key, child_keys_list)

            if datagroups:
                for data in datagroups:
                    if data["leaf_name"] not in [
                        "aol",
                        "images",
                        "private_net",
                        "sys_APM_MS_Office_OFBA_DG",
                    ]:
                        data["name"] = data["leaf_name"]
                        data["data_type"] = list_type_data[data["type"]]
                        del data["leaf_name"]
                        del data["type"]
                        list_values = []
                        for value in values:
                            if value["leaf_name"] == data["name"]:
                                list_values.append(
                                    {"name": value["value"], "data": value["data"]}
                                )
                        data["records"] = str(list_values)
                        data["comand"] = self.comands.comands_datagroup(datagroups=data)
                        sessao.add(DataGroupModel(**data, external_id=self.external_id))

            # irule
            root_key = "rule"
            child_keys_list = ["leaf_name", "definition", "partition_id"]
            irules = utils.json_parser(self.file, root_key, child_keys_list)

            if irules:
                for irule in irules:
                    if not irule["leaf_name"].startswith("_sys_"):
                        irule["name"] = irule["leaf_name"]
                        del irule["leaf_name"]
                        irule["comand"] = self.comands.comands_irule(rule=irule)
                        sessao.add(iRuleModel(**irule, external_id=self.external_id))
        sessao.commit()
        sessao.close()

    def create_register_database_monitor(self):
        sessao = self.session()
        if self.ssh:
            monitor_list = self.net_connect.send_command(
                "list ltm monitor non-default-properties one-line"
            )
            monitor_list = ltm_utils.find_and_get_prop_monitor(monitor_list)

            for monitor in monitor_list:
                monitor_model = MonitorModel(**monitor, external_id=self.external_id)
                sessao.add(monitor_model)
        else:
            root_key = "monitor"
            child_keys_list = [
                "leaf_name",
                "interval",
                "timeout",
                "get_defaults_from",
                "addr",
                "port",
                "partition_id",
            ]
            monitors = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "monitor_param"
            child_keys_list = ["leaf_name", "pkey", "pvalue"]
            monitor_parans = utils.json_parser(self.file, root_key, child_keys_list)

            for monitor in monitors:
                if monitor["get_defaults_from"] is not None:
                    monitor["name"] = monitor["leaf_name"]
                    monitor["defaultsFrom"] = monitor["get_defaults_from"]
                    monitor["destination"] = monitor["addr"]
                    del monitor["addr"]
                    del monitor["leaf_name"]
                    del monitor["get_defaults_from"]
                    for parans in monitor_parans:
                        if parans["leaf_name"] == monitor["name"]:
                            if parans["pkey"] == "SEND=":
                                monitor["send"] = parans["pvalue"]
                            elif parans["pkey"] == "RECV_I=":
                                monitor["recv"] = parans["pvalue"]
                            else:
                                continue
                    if "send" not in monitor.keys():
                        monitor["send"] = ""
                    if "recv" not in monitor.keys():
                        monitor["recv"] = ""
                    monitor["comand"] = self.comands.comands_monitor(monitor=monitor)
                    sessao.add(MonitorModel(**monitor, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_profiles(self):
        sessao = self.session()
        if self.ssh:
            profiles_list = self.net_connect.send_command(
                "list ltm profile non-default-properties one-line"
            )
            profiles_list = ltm_utils.find_and_get_prop_profiles(profiles_list)

            for profile in profiles_list:
                profiles_model = ProfilesSSLModel(
                    **profile, external_id=self.external_id
                )
                sessao.add(profiles_model)
        else:
            root_key = "profile_serverssl"
            child_keys_list = [
                "leaf_name",
                "default_name",
                "ciphers",
                "cert",
                "partition_id",
            ]
            profiles_serverssl = utils.json_parser(self.file, root_key, child_keys_list)

            # Profiles Client SSL
            root_key = "profile_clientssl"
            child_keys_list = [
                "leaf_name",
                "default_name",
                "ciphers",
                "cert",
                "partition_id",
            ]
            profiles_clientssl = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "profile_persist"
            child_keys_list = ["leaf_name", "default_name", "partition_id"]
            profiles_persist = utils.json_parser(self.file, root_key, child_keys_list)

            profiles_service = []
            for service in LIST_PROFILE_TYPES:
                root_key = f"profile_{service}"
                child_keys_list = ["leaf_name", "default_name", "partition_id"]
                list_result = utils.json_parser(self.file, root_key, child_keys_list)
                list_append = []
                for result in list_result:
                    result["service"] = service
                    list_append.append(result)
                profiles_service.extend(list_append)

            profiles_protocol = []
            for service in LIST_PROFILE_PROTO_TYPE:
                root_key = f"profile_{service}"
                child_keys_list = ["leaf_name", "default_name", "partition_id"]
                list_result = utils.json_parser(self.file, root_key, child_keys_list)
                list_append = []
                for result in list_result:
                    result["service"] = "fastl4" if service == "bigproto" else service
                    list_append.append(result)
                profiles_protocol.extend(list_append)

            profiles_other = []
            for service in PROFILES_OTHERS:
                root_key = f"{service}"
                child_keys_list = ["leaf_name", "default_name", "partition_id"]
                list_result = utils.json_parser(self.file, root_key, child_keys_list)
                list_append = []
                for result in list_result:
                    result["service"] = PROFILES_OTHERS_API[service]
                    list_append.append(result)
                profiles_other.extend(list_append)

            for profile in profiles_serverssl:
                if profile["leaf_name"] not in PROFILES_SSL_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["service"] = "server-ssl"
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="ssl"
                    )
                    sessao.add(
                        ProfilesSSLModel(**profile, external_id=self.external_id)
                    )

            for profile in profiles_clientssl:
                if profile["leaf_name"] not in PROFILES_SSL_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["service"] = "client-ssl"
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="ssl"
                    )
                    sessao.add(
                        ProfilesSSLModel(**profile, external_id=self.external_id)
                    )

            for profile in profiles_service:
                if profile["leaf_name"] not in PROFILES_SERVICES_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="service"
                    )
                    sessao.add(
                        ProfilesServicesModel(**profile, external_id=self.external_id)
                    )

            for profile in profiles_persist:
                if profile["leaf_name"] not in PROFILES_PERSIST_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["service"] = profile["default_name"][
                        profile["default_name"].rfind("/") + 1 :
                    ]
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="persist"
                    )
                    sessao.add(
                        ProfilesPersistModel(**profile, external_id=self.external_id)
                    )

            for profile in profiles_protocol:
                if profile["leaf_name"] not in PROFILES_PROTOCOL_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="protocol"
                    )
                    sessao.add(
                        ProfilesProtocolModel(**profile, external_id=self.external_id)
                    )

            for profile in profiles_other:
                if profile["leaf_name"] not in PROFILES_OTHER_IGNORE:
                    profile["name"] = profile["leaf_name"]
                    del profile["leaf_name"]
                    profile["comand"] = self.comands.comands_profiles(
                        profiles=profile, type="other"
                    )
                    sessao.add(
                        ProfilesOtherModel(**profile, external_id=self.external_id)
                    )

        sessao.commit()
        sessao.close()

    def create_register_database_policies(self):
        sessao = self.session()
        if self.ssh:
            policies_list = self.net_connect.send_command(
                "list ltm policy non-default-properties one-line"
            )
            policies_list = ltm_utils.find_and_get_prop_policies(policies_list)

            for policy in policies_list:
                polices_model = PoliciesModel(**policy, external_id=self.external_id)
                sessao.add(polices_model)

        else:
            root_key = "policy_base"
            child_keys_list = [
                "leaf_name",
                "status",
                "last_modified",
                "strategy",
                "partition_id",
            ]
            policies = utils.json_parser(self.file, root_key, child_keys_list)
            if policies:
                for policy in policies:
                    policy["name"] = policy["leaf_name"]
                    del policy["leaf_name"]
                    policy["strategy"] = policy["strategy"].split("/")
                    policy["strategy"] = policy["strategy"][2]
                    policy["comand"] = self.comands.comands_policies(policies=policy)
                    sessao.add(PoliciesModel(**policy, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_snat(self):
        sessao = self.session()
        if self.ssh:
            snats = self.net_connect.send_command("list ltm snat one-line")
            snats = ltm_utils.find_and_get_prop_snat(snats)

            for snat in snats:
                snat_model = SnatModel(**snat, external_id=self.external_id)
                sessao.add(snat_model)
        else:
            root_key = "snat"
            child_keys_list = [
                "leaf_name",
                "description",
                "trans_addr_name",
                "srcport" "auto_lasthop",
                "partition_id",
            ]
            snats = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "snat_vlan"
            child_keys_list = ["leaf_name", "vlan_name"]
            vlans = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "snat_orig_addr"
            child_keys_list = ["leaf_name", "addr", "wildmask"]
            origins = utils.json_parser(self.file, root_key, child_keys_list)
            if snats:
                for snat in snats:
                    snat["name"] = snat["leaf_name"]
                    del snat["leaf_name"]
                    list_vlan = [""]
                    for vlan in vlans:
                        if vlan["leaf_name"] == snat["name"]:
                            list_vlan.append(vlan["vlan_name"])

                    snat["vlans"] = str(list_vlan)
                    list_origins = []
                    for origin in origins:
                        if origin["leaf_name"] == snat["name"]:
                            list_origins.append(
                                {
                                    "name": f"{origin['addr']}/{utils.calculator_mask(origin['wildmask'])}"
                                }
                            )

                    snat["origins"] = str(list_origins)
                    snat["comand"] = self.comands.comands_snat(snat=snat)
                    sessao.add(SnatModel(**snat, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_snat_pool(self):
        sessao = self.session()

        if self.ssh:
            snats_pools = self.net_connect.send_command("list ltm snatpool one-line")
            snats_pools = ltm_utils.find_and_get_prop_snat_pool(snats_pools)

            for snats_pool in snats_pools:
                snatpool_model = SnatpoolModel(
                    **snats_pool, external_id=self.external_id
                )
                sessao.add(snatpool_model)
        else:
            root_key = "snatpool"
            child_keys_list = ["leaf_name", "partition_id"]
            snatpools = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "snatpool_trans_addr"
            child_keys_list = ["leaf_name", "trans_address"]
            members = utils.json_parser(self.file, root_key, child_keys_list)
            if snatpools:
                for snatpool in snatpools:
                    snatpool["name"] = snatpool["leaf_name"]
                    del snatpool["leaf_name"]
                    list_members = []
                    for member in members:
                        if member["leaf_name"] == snatpool["name"]:
                            list_members.append(member["trans_address"])
                    snatpool["members"] = str(list_members)
                    snatpool["comand"] = self.comands.comands_snat_pool(
                        snat_pool=snatpool
                    )
                    sessao.add(SnatpoolModel(**snatpool, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def create_register_database_nat(self):
        sessao = self.session()
        # nat
        if self.ssh:
            nats = self.net_connect.send_command("list ltm nat one-line")
            nats = ltm_utils.find_and_get_prop_nat(nats)

            for nat in nats:
                nat_model = NatModel(**nat, external_id=self.external_id)
                sessao.add(nat_model)
        else:
            root_key = "nat"
            child_keys_list = [
                "leaf_name",
                "trans_addr",
                "orig_addr",
                "traffic_group",
                "auto_lasthop",
                "partition_id",
            ]
            nats = utils.json_parser(self.file, root_key, child_keys_list)

            root_key = "nat_vlan"
            child_keys_list = ["leaf_name", "vlan_name"]
            nat_vlans = utils.json_parser(self.file, root_key, child_keys_list)
            if nats:
                for nat in nats:
                    nat["name"] = nat["leaf_name"]
                    del nat["leaf_name"]

                    list_vlan = []
                    for nat_vlan in nat_vlans:
                        if nat["name"] == nat_vlan["leaf_name"]:
                            list_vlan.append(nat_vlan["vlan_name"])

                    nat["vlans"] = str(list_vlan)
                nat["comand"] = self.comands.comands_nat(nat=nat)
                sessao.add(NatModel(**nat, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_pool_by_id(self, external_id):
        sessao = self.session()
        pools = (
            sessao.query(PoolModel)
            .filter(PoolModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_pool = []
        for pool in pools:
            list_pool.append(
                {
                    "id": pool.id,
                    "name": pool.name,
                    "description": pool.description,
                    "members": pool.members,
                    "loadBalancingMode": pool.loadBalancingMode,
                    "monitor": pool.monitor,
                    "external_id": pool.external_id,
                }
            )
        return list_pool

    def get_virtual_server_by_id(self, external_id):
        sessao = self.session()
        vitual_servers = (
            sessao.query(VirtualServersModel)
            .filter(VirtualServersModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_vitual_servers = []

        for vitual_server in vitual_servers:
            list_vitual_servers.append(
                {
                    "id": vitual_server.id,
                    "name": vitual_server.name,
                    "description": vitual_server.description,
                    "destination": vitual_server.destination,
                    "type": vitual_server.type,
                    "port": vitual_server.port,
                    "mask": vitual_server.mask,
                    "source": vitual_server.source,
                    "ip_proto": vitual_server.ip_proto,
                    "source_address_translation_type": vitual_server.source_address_translation_type,
                    "translate_addr": vitual_server.translate_addr,
                    "translate_port": vitual_server.translate_port,
                    "rulesReference": vitual_server.rulesReference,
                    "pool": vitual_server.pool,
                    "profilesReference": vitual_server.profilesReference,
                    "external_id": vitual_server.external_id,
                }
            )
        return list_vitual_servers

    def get_datagroup_by_id(self, external_id):
        sessao = self.session()
        datagroups = (
            sessao.query(DataGroupModel)
            .filter(DataGroupModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datagroups = []

        for datagroup in datagroups:
            list_datagroups.append(
                {
                    "id": datagroup.id,
                    "name": datagroup.name,
                    "data_type": datagroup.data_type,
                    "records": datagroup.records,
                    "external_id": datagroup.external_id,
                }
            )
        return list_datagroups

    def get_irule_by_id(self, external_id):
        sessao = self.session()
        irules = (
            sessao.query(iRuleModel)
            .filter(iRuleModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_irules = []

        for irule in irules:
            list_irules.append(
                {
                    "id": irule.id,
                    "name": irule.name,
                    "definition": irule.definition,
                    "external_id": irule.external_id,
                }
            )
        return list_irules

    def get_monitor_by_id(self, external_id):
        sessao = self.session()
        monitors = (
            sessao.query(MonitorModel)
            .filter(MonitorModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_monitors = []

        for monitor in monitors:
            list_monitors.append(
                {
                    "id": monitor.id,
                    "name": monitor.name,
                    "interval": monitor.interval,
                    "timeout": monitor.timeout,
                    "send": monitor.send,
                    "recv": monitor.recv,
                    "defaultsFrom": monitor.defaultsFrom,
                    "destination": monitor.destination,
                    "port": monitor.port,
                    "external_id": monitor.external_id,
                }
            )
        return list_monitors

    def get_profiles_by_id(self, external_id):
        sessao = self.session()
        profiles_ssl = (
            sessao.query(ProfilesSSLModel)
            .filter(ProfilesSSLModel.external_id == str(external_id))
            .all()
        )
        profiles_services = (
            sessao.query(ProfilesServicesModel)
            .filter(ProfilesServicesModel.external_id == str(external_id))
            .all()
        )
        profiles_persist = (
            sessao.query(ProfilesPersistModel)
            .filter(ProfilesPersistModel.external_id == str(external_id))
            .all()
        )
        profiles_protocol = (
            sessao.query(ProfilesProtocolModel)
            .filter(ProfilesProtocolModel.external_id == str(external_id))
            .all()
        )
        profiles_other = (
            sessao.query(ProfilesOtherModel)
            .filter(ProfilesOtherModel.external_id == str(external_id))
            .all()
        )

        sessao.close()
        list_profiles_ssl = []
        list_profiles_services = []
        list_profiles_persist = []
        list_profiles_protocol = []
        list_profiles_other = []

        for profile in profiles_ssl:
            list_profiles_ssl.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "default_name": profile.default_name,
                    "ciphers": profile.ciphers,
                    "cert": profile.cert,
                    "service": profile.service,
                    "external_id": profile.external_id,
                }
            )

        for profile in profiles_services:
            list_profiles_services.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "default_name": profile.default_name,
                    "partition_id": profile.partition_id,
                    "service": profile.service,
                    "external_id": profile.external_id,
                }
            )

        for profile in profiles_persist:
            list_profiles_persist.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "default_name": profile.default_name,
                    "partition_id": profile.partition_id,
                    "service": profile.service,
                    "external_id": profile.external_id,
                }
            )

        for profile in profiles_protocol:
            list_profiles_protocol.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "default_name": profile.default_name,
                    "partition_id": profile.partition_id,
                    "service": profile.service,
                    "external_id": profile.external_id,
                }
            )

        for profile in profiles_other:
            list_profiles_other.append(
                {
                    "id": profile.id,
                    "name": profile.name,
                    "default_name": profile.default_name,
                    "partition_id": profile.partition_id,
                    "service": profile.service,
                    "external_id": profile.external_id,
                }
            )
        return (
            list_profiles_ssl,
            list_profiles_services,
            list_profiles_persist,
            list_profiles_protocol,
            list_profiles_other,
        )

    def get_policies_by_id(self, external_id):
        sessao = self.session()
        policies = (
            sessao.query(PoliciesModel)
            .filter(PoliciesModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_policies = []

        for policie in policies:
            list_policies.append(
                {
                    "id": policie.id,
                    "name": policie.name,
                    "status": policie.status,
                    "last_modified": policie.last_modified,
                    "external_id": policie.external_id,
                }
            )
        return list_policies

    def get_snat_pool_by_id(self, external_id):
        sessao = self.session()
        snatpools = (
            sessao.query(SnatpoolModel)
            .filter(SnatpoolModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_snatpools = []

        for snatpool in snatpools:
            list_snatpools.append(
                {
                    "id": snatpool.id,
                    "name": snatpool.name,
                    "members": snatpool.members,
                    "external_id": snatpool.external_id,
                }
            )
        return list_snatpools

    def get_snat_by_id(self, external_id):
        sessao = self.session()
        snats = (
            sessao.query(SnatModel)
            .filter(SnatModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_snats = []

        for snat in snats:
            list_snats.append(
                {
                    "id": snat.id,
                    "name": snat.name,
                    "description": snat.description,
                    "trans_addr_name": snat.trans_addr_name,
                    "origins": snat.origins,
                    "srcport": snat.srcport,
                    "vlans": snat.vlans,
                    "auto_lasthop": snat.auto_lasthop,
                    "external_id": snat.external_id,
                }
            )
        return list_snats

    def get_nat_by_id(self, external_id):
        sessao = self.session()
        nats = (
            sessao.query(NatModel)
            .filter(NatModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_nats = []

        for nat in nats:
            list_nats.append(
                {
                    "id": nat.id,
                    "name": nat.name,
                    "trans_addr": nat.trans_addr,
                    "orig_addr": nat.orig_addr,
                    "traffic_group": nat.traffic_group,
                    "vlans": nat.vlans,
                    "auto_lasthop": nat.auto_lasthop,
                    "external_id": nat.external_id,
                }
            )
        return list_nats


class LtmMigrate:
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

    def create_pool(self, list_pools):

        dict_lb_method = {
            "0 - Round Robin": "round-robin",
            "1 - Ratio (member)": "ratio-member",
            "2 - Least Connections (member)": "least-connections-member",
            "3 - Observed (member)": "observed-member",
            "4 - Predictive (member)": "predictive-member",
            "5 - Ratio (node)": "ratio-node",
            "6 - Least Connections (node)": "least-connections-node",
            "7 - Fastest (node)": "fastest-node",
            "8 - Observed (node)": "observed-node",
            "9 - Predictive (node)": "predictive-node",
            "10 - Dynamic Ratio (node)": "dynamic-ratio-node",
            "11 - Fastest (application)": "fastest-application",
            "12 - Least Sessions": "least-sessions",
            "13 - Dynamic Ratio (member)": "dynamic-ratio-member",
            "15 - Weighted Least Connections (member)": "weighted-least-connections-member",
            "16 - Weighted Least Connections (node)": "weighted-least-connections-node",
            "17 - Ratio (session)": "ratio-session",
            "18 - Ratio Least Connections (member)": "ratio-least-connections-member",
            "19 - Ratio Least Connections (node)": "ratio-least-connections-node",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})
        for pool in list_pools:
            payload = {
                "name": pool["model"]["name"],
                "description": pool["model"]["description"],
                "partition": pool["model"]["partition_id"],
                "monitor": pool["model"]["monitor"],
                "loadBalancingMode": dict_lb_method[pool["model"]["loadBalancingMode"]],
                "members": ast.literal_eval(pool["model"]["members"]),
            }

            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/pool", data=json.dumps(payload)
            )
            self._save_register(
                payload=payload,
                internal_id=pool["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="pool",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="pool",
                name_service=pool["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_virtual_server(self, list_virtual_server):
        dict_ip_proto = {
            "1 - * All Protocols": "",
            "6 - TCP": "tcp",
            "17 - UDP": "udp",
            "132 - SCTP": "sctp",
            "50 - IPsec ESP": "ipsec-esp",
            "51 - IPsec AH": "ipsec-ah",
        }
        dict_sour_add_trans = {
            "1 - SNAT": "snat",
            "3 - Auto Map": "automap",
            "0 - None": None,
        }
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }

        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})
        for virtual_server in list_virtual_server:
            payload = {
                "name": virtual_server["model"]["name"],
                "description": virtual_server["model"]["description"],
                "destination": f"{virtual_server['model']['destination']}:{virtual_server['model']['port']}",
                "mask": virtual_server["model"]["mask"],
                "source": f"{virtual_server['model']['source']}/0",
                "ipProtocol": dict_ip_proto[virtual_server["model"]["ip_proto"]],
                "sourceAddressTranslation": {
                    "type": dict_sour_add_trans[
                        virtual_server["model"]["source_address_translation_type"]
                    ],
                },
                "translateAddress": dict_enable[
                    virtual_server["model"]["translate_addr"]
                ],
                "translatePort": dict_enable[virtual_server["model"]["translate_port"]],
                "rules": ast.literal_eval(virtual_server["model"]["rulesReference"]),
                "pool": virtual_server["model"]["pool"],
                "profiles": ast.literal_eval(
                    virtual_server["model"]["profilesReference"]
                ),
                "partition": virtual_server["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/virtual", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=virtual_server["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="virtual_server",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="virtual_server",
                name_service=virtual_server["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_irule(self, list_irule):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for irule in list_irule:

            payload = {
                "name": irule["model"]["name"],
                "apiAnonymous": irule["model"]["definition"],
                "partition": irule["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/rule/", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=irule["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="irule",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="irule",
                name_service=irule["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

        # corrigir os dados

    def create_datagroup(self, list_datagroups):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for datagroup in list_datagroups:
            payload = {
                "name": datagroup["model"]["name"],
                "type": datagroup["model"]["data_type"],
                "records": ast.literal_eval(datagroup["model"]["records"]),
                "partition": datagroup["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/data-group/internal/",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=datagroup["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="datagroup",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="datagroup",
                name_service=datagroup["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_monitor(self, list_monitor):

        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for monitor in list_monitor:
            type_monitor = monitor["model"]["defaultsFrom"]
            type_monitor = type_monitor.replace("/Common/", "")
            payload = {
                "name": monitor["model"]["name"],
                "interval": monitor["model"]["interval"],
                "timeout": monitor["model"]["timeout"],
                "recv": monitor["model"]["recv"],
                "send": monitor["model"]["send"],
                "destination": f"{monitor['model']['destination']}:{monitor['model']['port']}",
                "partition": monitor["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/monitor/{type_monitor}/",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=monitor["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="monitor",
            )

            monitor_big.send_status_process_import(
                status=result.status_code,
                service="monitor",
                name_service=monitor["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_snat(self, list_snat):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
            None: "default",
        }
        dict_srcport = {
            "0": "preserve",
            "1": "preserve-strict",
            "2": "change",
            None: "preserve",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for snat in list_snat:
            vlan = ast.literal_eval(snat["model"]["vlans"])
            vlan = list(filter(bool, vlan))
            payload = {
                "name": snat["model"]["name"],
                "description": snat["model"]["description"],
                "sourcePort": dict_srcport[snat["model"]["srcport"]],
                "autoLasthop": dict_enable[snat["model"]["auto_lasthop"]],
                "translation": snat["model"]["trans_addr_name"],
                "origins": ast.literal_eval(snat["model"]["origins"]),
                "vlans": vlan,
                "partition": snat["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/snat/", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=snat["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="snat",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="snat",
                name_service=snat["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_snat_pool(self, list_snat_pool):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for snat_pool in list_snat_pool:
            payload = {
                "name": snat_pool["model"]["name"],
                "members": ast.literal_eval(snat_pool["model"]["members"]),
                "partition": snat_pool["model"]["partition_id"],
            }

            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/snatpool/", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=snat_pool["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="snat_pool",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="snat_pool",
                name_service=snat_pool["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_nat(self, list_nat):
        dict_enable = {
            "0": "disabled",
            "1": "enabled",
        }
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for nat in list_nat:
            payload = {
                "name": nat["model"]["name"],
                "autoLasthop": dict_enable[nat["model"]["auto_lasthop"]],
                "trafficGroup": nat["model"]["traffic_group"],
                "originatingAddress": nat["model"]["orig_addr"],
                "translationAddress": nat["model"]["trans_addr"],
                "vlans": ast.literal_eval(nat["model"]["vlans"]),
                "partition": nat["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/nat/", data=json.dumps(payload)
            )

            self._save_register(
                payload=payload,
                internal_id=nat["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="nat",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="nat",
                name_service=nat["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_policies(self, list_policies):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for policy in list_policies:
            payload = {
                "name": policy["model"]["name"],
                "strategy": policy["model"]["strategy"],
                "subPath": "Drafts",
                "partition": policy["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/policy/", data=json.dumps(payload)
            )
            self._save_register(
                payload=payload,
                internal_id=policy["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="policy",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="policy",
                name_service=policy["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_profile_ssl(self, list_profile):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for profile in list_profile:
            type_ssl = profile["model"]["service"]
            payload = {
                "name": profile["model"]["name"],
                "partition": profile["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/profile/{type_ssl}",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=profile["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="profile",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="profile",
                name_service=profile["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_profile_services(self, list_profile):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for profile in list_profile:
            type_service = (
                "sip"
                if profile["model"]["service"] == "sipp"
                else profile["model"]["service"]
            )
            payload = {
                "name": profile["model"]["name"],
                "partition": profile["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/profile/{type_service}",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=profile["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="profile",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="profile",
                name_service=profile["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_profile_persist(self, list_profile):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for profile in list_profile:
            type_persist = profile["model"]["service"].replace("_", "-")
            payload = {
                "name": profile["model"]["name"],
                "partition": profile["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/persistence/{type_persist}",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=profile["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="profile",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="profile",
                name_service=profile["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_profile_other(self, list_profile):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})

        for profile in list_profile:
            payload = {
                "name": profile["model"]["name"],
                "partition": profile["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/profile/{profile['model']['service']}",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=profile["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="profile",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="profile",
                name_service=profile["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)

    def create_profile_protocol(self, list_profile):
        session = requests.session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json"})
        for profile in list_profile:
            payload = {
                "name": profile["model"]["name"],
                "partition": profile["model"]["partition_id"],
            }
            result = session.post(
                f"https://{self.host}/mgmt/tm/ltm/profile/{profile['model']['service']}",
                data=json.dumps(payload),
            )

            self._save_register(
                payload=payload,
                internal_id=profile["model"]["id"],
                status_code=result.status_code,
                reason=result.text,
                service="profile",
            )
            monitor_big.send_status_process_import(
                status=result.status_code,
                service="profile",
                name_service=profile["model"]["name"],
                reason=result.text,
            )
            time.sleep(0.2)


class LtmCreateComandsTmsh:
    def __init__(self, external_id):
        self.external_id = external_id

    @staticmethod
    def comands_pools(pool):
        comand = f"create ltm pool /{pool['partition_id']}/{pool['name']} members add "
        members = "{"
        for member in ast.literal_eval(pool["members"]):
            members += " " + member["name"] + " "
        comand = comand + members + " }"
        if pool["monitor"] is not None:
            comand += f" monitor {pool['monitor']}"
        return comand

    @staticmethod
    def comands_virtual_server(vs):
        dict_ip_proto = {
            "1 - * All Protocols": "",
            "6 - TCP": "tcp",
            "17 - UDP": "udp",
            "132 - SCTP": "sctp",
            "50 - IPsec ESP": "ipsec-esp",
            "51 - IPsec AH": "ipsec-ah",
        }
        comand = f"create ltm virtual /{vs['partition_id']}/{vs['name']} pool {vs['pool']} source {vs['source']} description {vs['description']} profiles add "
        profiles = "{"
        for profile in ast.literal_eval(vs["profilesReference"]):
            profiles += " " + profile + " "
        comand = comand + profiles + " }"

        comand += f" ip-protocol {dict_ip_proto[vs['ip_proto']]} "
        comand += f" destination {vs['destination']}:{vs['port']}"
        comand += f" mask {vs['mask']}"

        if ast.literal_eval(vs["rulesReference"]) != []:
            rules = " rules {"
            for rule in ast.literal_eval(vs["rulesReference"]):
                rules += " " + rule + " "
            comand = comand + rules + " }"

        return comand

    @staticmethod
    def comands_irule(rule):
        comand = f"create ltm rule /{rule['partition_id']}/{rule['name']}"
        return comand

    @staticmethod
    def comands_datagroup(datagroups):
        comands = f"create ltm data-group internal /{datagroups['partition_id']}/{datagroups['name']} type {datagroups['data_type']} "
        if ast.literal_eval(datagroups["records"]) != []:
            rec = "records add{"
            for record in ast.literal_eval(datagroups["records"]):
                rec += f" {record['name']} " + "{" + f" {record['data']} " + "}"
            comands += rec
        return comands

    @staticmethod
    def comands_monitor(monitor):
        comands = f"create ltm monitor {monitor['defaultsFrom']} /{monitor['partition_id']}/{monitor['name']}"
        comands += f" send {monitor['send']} recv {monitor['recv']} timeout {monitor['timeout']} interval {monitor['interval']}"
        comands += f" destination {monitor['destination']}:{monitor['port']} "
        return comands

    @staticmethod
    def comands_policies(policies):
        comand = f"create ltm policy /{policies['partition_id']}/{policies['name']} strategy {policies['strategy']}"
        return comand

    @staticmethod
    def comands_snat_pool(snat_pool):
        comands = f"create ltm snatpool /{snat_pool['partition_id']}/{snat_pool['name']} members add"

        if ast.literal_eval(snat_pool["members"]) != []:
            members = " {"
            for member in ast.literal_eval(snat_pool["members"]):
                members += " " + member + " "
            comands += members
        return comands

    @staticmethod
    def comands_snat(snat):
        comand = f"create ltm snat /{snat['partition_id']}/{snat['name']} translation {snat['trans_addr_name']}"
        comand += f" source-port {snat['srcport']} origins {snat['origins']} auto-lasthop {snat['auto_lasthop']}"
        if ast.literal_eval(snat["vlans"]) != []:
            comand += " vlans-enabled vlans add {"
            for vlan in ast.literal_eval(snat["vlans"]):
                comand += " " + vlan + " "
            comand += "}"
        return comand

    @staticmethod
    def comands_nat(nat):
        comand = f"create ltm nat /{nat['partition_id']}/{nat['name']} translation-address {nat['trans_addr']} originating-address {nat['orig_addr']} "
        comand += (
            f"traffic-group {nat['traffic_group']} auto-lasthop {nat['auto_lasthop']}"
        )

        if ast.literal_eval(nat["vlans"]) != []:
            comand += " vlans-enabled vlans add {"
            for vlan in ast.literal_eval(nat["vlans"]):
                comand += " " + vlan + " "
            comand += "} "
        return comand

    @staticmethod
    def comands_profiles(profiles, type):
        if type == "persist":
            comand = f"create ltm persistence {profiles['service']} /{profiles['partition_id']}/{profiles['name']}"
        else:
            comand = f"create ltm profile {profiles['service']} /{profiles['partition_id']}/{profiles['name']}"
        return comand
