import os
import ast
import gzip
import shutil
import tarfile
import ipaddress

import xmltodict

DICT_DEPENDENCIAS = {
    "virtual_server": ["pool", "irule", "folder"],
    "pool": ["monitor", "folder"],
    "vlan": [],
    "monitor": ["folder"],
    "irule": ["folder"],
    "datagroup": ["folder"],
    "folder": ["traffic_group", "route_domain"],
    "self_ip": ["traffic_group", "vlan"],
    "route_domain": ["vlan"],
    "static_route": ["self_ip"],
    "policies": ["folder"],
    "traffic_group": [],
    "protocol": [],
    "transport_config": ["irule", "protocol"],
    "peer": ["pool", "transport_config"],
    "route": ["router"],
    "router": [],
    "profiles_services": ["folder"],
    "profiles_ssl": ["folder"],
    "profiles_other": ["folder"],
    "profiles_protocol": ["folder"],
    "profiles_persist": ["folder"],
    "default": [],
    "user_alert": [],
    "icall": [],
    "snat_pool": ["folder"],
    "nat": ["folder"],
    "snat": ["folder"],
}

DICT_EXCLUDE = [
    "Common",
    "http",
    "https",
    "udp",
    "tcp",
    "/Common/traffic-group-1",
    "/Common/traffic-group-local-only",
    "default",
    "0",
    "_sys_https_redirect",
    "http-tunnel",
    "socks-tunnel",
    "gateway_icmp",
    "None",
    None,
    "https_443",
    "0",
]


class BigIpUtils:
    def get_version(self, version: str):
        version = version.split("\n")
        version = version[1].split(" ")
        version = list(filter(bool, version))
        return version[1]

    def get_hostname(self, hostname: str):
        hostname = hostname.split(" ")
        hostname = list(filter(bool, hostname))
        return hostname[1]

    def get_ntp_servers(self, ntp_server):
        ntp_server = ntp_server.replace("{", "").replace("servers", "").replace("}", "")
        ntp_server = ntp_server.split(" ")
        ntp_server = list(filter(bool, ntp_server))
        return ntp_server

    def get_ntp_timezone(self, ntp_timezone):
        ntp_timezone = ntp_timezone.replace("timezone", "")
        ntp_timezone = ntp_timezone.replace(" ", "")
        return ntp_timezone

    def get_dns_name_servers(self, dns_name_servers):
        dns_name_servers = (
            dns_name_servers.replace("{", "")
            .replace("name-servers", "")
            .replace("}", "")
        )
        dns_name_servers = dns_name_servers.split(" ")
        dns_name_servers = list(filter(bool, dns_name_servers))
        return dns_name_servers

    def get_dns_search(self, dns_search):
        dns_search = (
            dns_search.replace("{", "")
            .replace("search", "")
            .replace("}", "")
            .replace(" ", "")
        )
        return dns_search

    def get_ip_management(self, ip_management):
        ip_management = (
            ip_management.replace("sys management-ip", "")
            .replace("{", "")
            .replace(" ", "")
        )
        return ip_management

    def get_gateway(self, gateway):
        gateway = gateway.replace("gateway", "").replace("{", "").replace(" ", "")
        return gateway

    def get_snmp_contact(self, snmp_contact):
        snmp_contact = snmp_contact.replace("sys-contact", "").replace(" ", "")
        return snmp_contact

    def get_snmp_location(self, snmp_location):
        snmp_location = snmp_location.replace("sys-location", "").replace(" ", "")
        return snmp_location

    def get_snmp_allowed(self, snmp_allowed):
        snmp_allowed = (
            snmp_allowed.replace("{", "")
            .replace("allowed-addresses", "")
            .replace("}", "")
        )
        snmp_allowed = snmp_allowed.split(" ")
        snmp_allowed = list(filter(bool, snmp_allowed))
        return snmp_allowed


class LtmUtils:
    def find_pool_name_tmsh(self, result: str):

        list_pool = []
        list_result = result.split("\n")

        for res in list_result:
            if res.find("pool_") > -1:
                list_pool.append(res[res.find("pool_") : res.find("{") - 1])

        return list_pool

    def get_propert_pool(self, members: str, load_balance: str, monitor: str):
        members = members.replace(" ", "")
        members = members.replace("{", "")
        members = members.split("\n")

        load_balance = load_balance.split("load-balancing-mode ")
        load_balance = load_balance[1]

        monitor = monitor.split("monitor ")
        monitor = monitor[1]

        return members, load_balance, monitor

    def find_vs_tmsh(self, result: str):

        list_vs = []
        result = result.replace(" {", "")
        list_result = result.split("\n")

        for res in list_result:

            vs = res.split("ltm virtual ")
            list_vs.append(vs[1])

        return list_vs

    def get_prop_vs(
        self,
        destination: str,
        mask: str,
        source: str,
        ipProtocol: str,
        sourceAddressTranslation: str,
        translateAddress: str,
        translatePort: str,
        rulesReference: str,
        pool: str,
        profilesReference: str,
        policies: str = None,
    ):
        dict_return = {}
        destination = destination.split("destination ")
        destination = destination[1]
        dict_return["destination"] = destination

        mask = mask.split("mask ")
        mask = mask[1]
        dict_return["mask"] = mask

        source = source.split("\n")
        source = source[0]
        source = source.split("source ")
        dict_return["source"] = source[1]

        ipProtocol = ipProtocol.split("ip-protocol ")
        ipProtocol = ipProtocol[1]
        dict_return["ipProtocol"] = ipProtocol

        if sourceAddressTranslation:
            sourceAddressTranslation = sourceAddressTranslation.split("type ")
            sourceAddressTranslation = sourceAddressTranslation[1]
        dict_return["sourceAddressTranslation"] = sourceAddressTranslation
        translateAddress = translateAddress.split("translate-address ")
        translateAddress = translateAddress[1]
        dict_return["translateAddress"] = translateAddress
        translatePort = translatePort.split("translate-port ")
        translatePort = translatePort[1]
        dict_return["translatePort"] = translatePort

        rulesReference = rulesReference.replace(" {", "")
        rulesReference = rulesReference[rulesReference.find("rules") :]
        rulesReference = rulesReference.replace(" ", "")
        rulesReference = rulesReference.replace("}", "")
        rulesReference = rulesReference.split("\n")

        cont = 0
        while cont < len(rulesReference):
            if rulesReference[cont] == "rules":
                del rulesReference[cont]
                continue
            elif rulesReference[cont] == "":
                del rulesReference[cont]
                continue
            cont += 1

        dict_return["rulesReference"] = rulesReference

        pool = pool.split("pool ")
        pool = pool[1]
        dict_return["pool"] = pool

        profilesReference = profilesReference.replace(" {", "")
        profilesReference = profilesReference[profilesReference.find("profiles") :]
        profilesReference = profilesReference.replace(" ", "")
        profilesReference = profilesReference.replace("}", "")
        profilesReference = profilesReference.split("\n")
        del profilesReference[0]

        dict_return["profilesReference"] = profilesReference

        if policies:
            pass

        return dict_return
        # Verificar as polices não consegui criar.

    def find_rule(self, result: str):
        list_rule = []
        list_result = result.split("\n")
        for res in list_result:
            list_rule.append(res[9 : res.find("{") - 1])
        return list_rule

    def get_irule(self, irule: str):
        irule = irule[irule.find("{") : len(irule)]
        return irule

    def find_and_get_prop_datagroup(datagroup: str):
        datagroup = datagroup.split("ltm data-group internal ")
        list_datagroup = []
        del datagroup[0]
        for data in datagroup:
            name = data[0 : data.find("{") - 1]
            records = data.split("records")
            del records[0]
            data_type = records[0].split("type ")
            records = data_type[0]
            data_type = data_type[1].replace(" }\n", "")

            list_records = []
            if "data" in records:
                records = records.replace(" ", "")
                records = records.split("}")

                for record in records:
                    if record != "":
                        record = record.replace("{", "").replace("{", "")
                        record = record.split("data")
                        dict_records = {"name": record[0], "data": record[1]}
                        list_records.append(dict_records)
            else:
                records = records.replace(" ", "")
                records = records[1 : len(records) - 1]
                records = records.split("{}")
                for record in records:
                    dict_records = {"name": record, "data": ""}
                    list_records.append(dict_records)

            dict_data = {
                "name": name,
                "data_type": data_type,
                "records": str(list_records),
            }

            list_datagroup.append(dict_data)

        return list_datagroup

    @staticmethod
    def encontrar_proximo_vazio(string, indice):
        tamanho = len(string)
        while indice < tamanho:
            if string[indice] == " ":
                return indice
            indice += 1
        return -1

    def find_and_get_prop_monitor(self, monitors):
        monitors = monitors.split("ltm monitor ")
        del monitors[0]
        list_monitors = []

        for monitor in monitors:
            name = monitor[0 : monitor.find("{")]
            name = name[name.find(" ") :]
            name = name.replace(" ", "")
            defaultsFrom = monitor[: monitor.find(" ")]

            send = monitor[
                monitor.find("send")
                + 5 : self.encontrar_proximo_vazio(monitor, monitor.find("send") + 5)
            ]
            recv = monitor[
                monitor.find("recv")
                + 5 : self.encontrar_proximo_vazio(monitor, monitor.find("recv") + 5)
            ]
            destination = monitor[
                monitor.find("destination")
                + 12 : self.encontrar_proximo_vazio(
                    monitor, monitor.find("destination") + 12
                )
            ]
            interval = monitor[
                monitor.find("interval")
                + 9 : self.encontrar_proximo_vazio(
                    monitor, monitor.find("interval") + 9
                )
            ]
            timeout = monitor[
                monitor.find("timeout")
                + 8 : self.encontrar_proximo_vazio(monitor, monitor.find("timeout") + 8)
            ]

            data = {
                "name": name,
                "defaultsFrom": defaultsFrom,
                "send": send,
                "recv": recv,
                "destination": destination,
                "interval": interval,
                "timeout": timeout,
            }
            list_monitors.append(data)

        return list_monitors

    def find_and_get_prop_profiles(self, profiles):
        profiles = profiles.split("ltm profile ")
        del profiles[0]
        list_profiles = []

        for profile in profiles:
            name = profile[0 : profile.find("{")]
            name = name[name.find(" ") :]
            name = name.replace(" ", "")
            type_profile = profile[: profile.find(" ")]

            profile = profile[profile.find("{") + 1 : profile.find("\n") - 1]
            profile = profile.split(" ")

            list_at = []
            cont = 0

            while cont < len(profile):
                if profile[cont] != "":
                    data = {"name": profile[cont], "value": profile[cont + 1]}
                    list_at.append(data)
                    cont += 2
                    continue

                cont += 1

            list_profiles.append(
                {
                    "name": name,
                    "type_profile": type_profile,
                    "list_attributes": str(list_at),
                }
            )

        return list_profiles

    def find_and_get_prop_policies(self, prolicies):
        prolicies = prolicies.split("ltm policy ")
        prolicies = list(filter(bool, prolicies))
        list_prolicies = []

        for policy in prolicies:
            name = policy[0 : policy.find("{") - 1]

            policy = policy[policy.find("{") + 1 : policy.find("\n") - 1]
            policy = policy.split(" ")

            list_at = []
            cont = 0

            while cont < len(policy):
                if policy[cont] != "":
                    data = {"name": policy[cont], "value": policy[cont + 1]}
                    list_at.append(data)
                    cont += 2
                    continue
                cont += 1

            list_prolicies.append({"name": name, "list_attributes": str(list_at)})

        return list_prolicies

    def find_and_get_prop_snat(self, snats):
        snats = snats.split("ltm snat ")
        snats = list(filter(bool, snats))
        list_snat = []

        for snat in snats:
            name = snat[0 : snat.find("{") - 1]

            auto_lasthop = snat[
                snat.find("auto-lasthop")
                + 13 : self.encontrar_proximo_vazio(
                    snat, snat.find("auto-lasthop") + 13
                )
            ]

            description = snat[snat.find("description") + 12 : snat.find("origins")]

            translation = snat[
                snat.find("translation")
                + 12 : self.encontrar_proximo_vazio(snat, snat.find("translation") + 12)
            ]
            source_port = snat[
                snat.find("source-port")
                + 12 : self.encontrar_proximo_vazio(snat, snat.find("source-port") + 12)
            ]

            vlans = snat[snat.find("vlans") : -2]
            vlans = vlans.split("{")
            lans = vlans[1].split("}")
            vlan = lans[1].replace(" ", "")
            lans = lans[0].split(" ")
            lans = list(filter(bool, lans))

            origins = snat[snat.find("origins") : snat.find("} }")]
            origins = origins.replace(" ", "")
            origins = origins.replace("{", " ")
            origins = origins[8:]
            origins = origins.replace(" ", "")
            origins = origins.split("}")

            list_snat.append(
                {
                    "name": name,
                    "auto_lasthop": auto_lasthop,
                    "description": description,
                    "translation": translation,
                    "source_port": source_port,
                    "vlans": str([{"vlan": vlan, "list_vlan": lans}]),
                    "origins": origins,
                }
            )

        return list_snat

    def find_and_get_prop_snat_pool(self, snat_pool):
        snat_pools = snat_pool.split("ltm snatpool ")
        snat_pools = list(filter(bool, snat_pools))
        list_snat_pool = []

        for snat_pool in snat_pools:
            name = snat_pool[0 : snat_pool.find(" ") - 1]
            members = snat_pool[snat_pool.find("members") :]
            members = members.replace("\n", "")
            members = members.split(" ")

            list_member = []
            for member in members:
                if member not in ["{", "}", "members"]:
                    list_member.append(member)

            list_snat_pool.append({"name": name, "members": str(list_member)})

        return list_snat_pool

    def find_and_get_prop_nat(self, nats):
        nats = nats.split("ltm nat ")
        nats = list(filter(bool, nats))
        list_snat = []

        for nat in nats:
            name = nat[: nat.find("{") - 1]
            auto_lasthop = nat[
                nat.find("auto-lasthop")
                + 13 : self.encontrar_proximo_vazio(nat, nat.find("auto-lasthop") + 13)
            ]
            originating_address = nat[
                nat.find("originating-address")
                + 20 : self.encontrar_proximo_vazio(
                    nat, nat.find("originating-address") + 20
                )
            ]
            traffic_group = nat[
                nat.find(" traffic-group")
                + 15 : self.encontrar_proximo_vazio(
                    nat, nat.find(" traffic-group") + 15
                )
            ]
            translation_address = nat[
                nat.find("translation-address")
                + 20 : self.encontrar_proximo_vazio(
                    nat, nat.find("translation-address") + 20
                )
            ]

            vlans = nat[nat.find("vlans") :]
            vlans = vlans.replace("\n", "")
            vlans = vlans.split(" ")

            list_vlans = []
            vlans_enabled = ""
            for vlan in vlans:
                if vlan not in ["{", "}", "vlans"]:
                    if vlan == "vlans-enabled":
                        vlans_enabled = vlan
                    else:
                        list_vlans.append(vlan)

            list_snat.append(
                {
                    "name": name,
                    "auto_lasthop": auto_lasthop,
                    "originating_address": originating_address,
                    "traffic_group": traffic_group,
                    "translation_address": translation_address,
                    "vlans": str(list_vlans),
                    "vlans_enabled": vlans_enabled,
                }
            )

        return list_snat


class UtilsUtils:
    @staticmethod
    def get_xml_from_qkview(QKVIEW_PATH, MCP_PATH, file_name, id):
        file_name_without_extension = file_name.replace(".qkview", "")

        # Ler o arquivo QKVIEW e extrair o arquivo .tar;
        with gzip.open(os.path.join(QKVIEW_PATH, file_name), "rb") as f_in:
            with open(
                os.path.join(QKVIEW_PATH, f"{file_name_without_extension}.tar"),
                "wb",
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.mkdir(os.path.join(MCP_PATH, id))

        with tarfile.open(
            os.path.join(QKVIEW_PATH, f"{file_name_without_extension}.tar"),
            "r:",
        ) as tar:
            xml_file = tar.extractfile("mcp_module.xml")
            users_file = tar.extractfile("config/bigip_user.conf")
            user_alert = tar.extractfile("config/user_alert.conf")

            # Ler o arquivo mcp_module.xml e armazenando dentro da pasta MCP com o nome do arquivo
            with open(
                os.path.join(MCP_PATH, id + f"/{file_name_without_extension}.xml"),
                "wb",
            ) as outfile:
                outfile.write(xml_file.read())
            with open(os.path.join(MCP_PATH, id + "/bigip_user.conf"), "wb") as outfile:
                outfile.write(users_file.read())

            with open(os.path.join(MCP_PATH, id + "/user_alert.conf"), "wb") as outfile:
                outfile.write(user_alert.read())

        with open(
            os.path.join(MCP_PATH, id + f"/{file_name_without_extension}.xml"),
            encoding="utf8",
        ) as xml_file:
            file_xml = xmltodict.parse(xml_file.read())

        with open(
            os.path.join(MCP_PATH, id + "/bigip_user.conf"), encoding="utf8"
        ) as file:
            users_file = file.read()

        with open(
            os.path.join(MCP_PATH, id + "/user_alert.conf"), encoding="utf8"
        ) as file:
            user_alert = file.read()

        os.remove(os.path.join(QKVIEW_PATH, f"{file_name_without_extension}.tar"))
        os.remove(os.path.join(QKVIEW_PATH, f"{file_name_without_extension}.qkview"))
        os.remove(os.path.join(MCP_PATH, id + f"/{file_name_without_extension}.xml"))
        os.remove(os.path.join(MCP_PATH, id + "/bigip_user.conf"))

        return file_xml, users_file, user_alert

    @staticmethod
    def json_parser(xml_to_json_file, root_key, child_keys_list):
        processed_data = []
        try:
            root_data = xml_to_json_file["Qkproc"][root_key]

            # Se a  root key estiver na lista de elementos
            if type(root_data) == list:
                for data in root_data:
                    value_return = {}
                    for chave, valor in data.items():
                        if chave in child_keys_list:
                            value_return[chave] = valor
                    processed_data.append(value_return)
            else:
                value_return = {}
                for chave, valor in root_data.items():
                    if chave in child_keys_list:
                        value_return[chave] = valor
                processed_data.append(value_return)
            return processed_data
        except Exception:
            print("não encontrado")
            return processed_data

    @staticmethod
    def calculator_mask(mask):
        dict_mask = {
            "0.0.0.0": "0",
            "255.0.0.0": "8",
            "255.128.0.0": "9",
            "255.192.0.0": "10",
            "255.224.0.0": "11",
            "255.240.0.0": "12",
            "255.248.0.0": "13",
            "255.252.0.0": "14",
            "255.254.0.0": "15",
            "255.255.0.0": "16",
            "255.255.128.0": "17",
            "255.255.192.0": "18",
            "255.255.224.0": "19",
            "255.255.240.0": "20",
            "255.255.248.0": "21",
            "255.255.252.0": "22",
            "255.255.254.0": "23",
            "255.255.255.0": "24",
            "255.255.255.128": "25",
            "255.255.255.192": "26",
            "255.255.255.224": "27",
            "255.255.255.240": "28",
            "255.255.255.248": "29",
            "255.255.255.252": "30",
            "255.255.255.254": "31",
            "255.255.255.255": "32",
        }
        return dict_mask[mask]


class Validate:
    @staticmethod
    def _verificar_ip_dentro_do_range(ip, rede, mascara):
        try:
            endereco_ip = ipaddress.IPv4Address(ip)
            rede = ipaddress.IPv4Network(rede + "/" + mascara, strict=False)
            return endereco_ip in rede
        except ipaddress.AddressValueError:
            return False

    def validate(self, list_objects: dict):
        keys = list_objects.keys()
        list_errors = []
        for key in keys:
            dependencias = DICT_DEPENDENCIAS[key]
            for data in list_objects[key]:
                dict_values = {}
                if key == "virtual_server":
                    dict_values["irule"] = (
                        []
                        if data["rulesReference"] is None
                        else ast.literal_eval(data["rulesReference"])
                    )
                    pool = [] if data["pool"] is None else data["pool"].split("/")
                    dict_values["pool"] = "" if pool == [] else pool[len(pool) - 1]
                    dict_values["folder"] = data["partition_id"]

                elif key == "pool":
                    dict_values["folder"] = data["partition_id"]
                    monitor = "" if data["monitor"] is None else data["monitor"]
                    monitor = (
                        monitor.replace("min 1 of ", "")
                        if monitor.startswith("min 1 of")
                        else monitor
                    )
                    monitor = (
                        monitor.replace("and ", "").split(" ")
                        if " and " in monitor
                        else monitor
                    )
                    dict_values["monitor"] = []
                    if type(monitor) == list:
                        for value in monitor:
                            value = value.split("/")
                            value = value[len(value) - 1]
                            value.replace(" ", "")
                            dict_values["monitor"].append(value)
                    else:
                        if monitor is None or monitor == "":
                            dict_values["monitor"] = monitor
                        else:
                            monitor = monitor.replace(" ", "").split("/")
                            monitor = monitor[len(monitor) - 1]
                            dict_values["monitor"] = monitor

                elif key in [
                    "monitor",
                    "irule",
                    "datagroup",
                    "policies",
                    "profiles_services",
                    "profiles_ssl",
                    "profiles_other",
                    "profiles_protocol",
                    "profiles_persist",
                ]:
                    dict_values["folder"] = data["partition_id"]

                elif key == "self_ip":
                    dict_values["traffic_group"] = data["traffic_group"]
                    dict_values["vlan"] = data["vlan"].split("/")[
                        len(data["vlan"].split("/")) - 1
                    ]

                elif key == "route_domain":
                    dict_values["vlan"] = []
                    vlan = ast.literal_eval(data["vlans"])
                    for value in vlan:
                        value = value.split("/")[len(value.split("/")) - 1].replace(
                            " ", ""
                        )
                        dict_values["vlan"].append(value)
                elif key == "static_route":
                    dict_values["self_ip"] = (
                        data["gateway"]
                        if "%" not in data["gateway"]
                        else data["gateway"][: data["gateway"].rfind("%")]
                    )
                else:
                    break

                for depencia in dependencias:
                    if (
                        dict_values[depencia] == ""
                        or dict_values[depencia] is None
                        or dict_values[depencia] in DICT_EXCLUDE
                    ):
                        continue
                    elif depencia == "self_ip" and key == "static_route":

                        def valida(x, y, z):
                            return self._verificar_ip_dentro_do_range(
                                ip=x, rede=y, mascara=z
                            )

                        list_verification = list(
                            map(
                                lambda d: valida(
                                    y=d["ip_addr"][: d["ip_addr"].rfind("%")],
                                    x=dict_values[depencia],
                                    z=d["net_mask"],
                                ),
                                list_objects[depencia],
                            ),
                        )
                        if True in list_verification:
                            continue
                        else:
                            list_errors.append(
                                [
                                    f"{key} -> {data['name']}: O gateway de rota estática {dict_values[depencia]} não está conectado diretamente por meio de uma interface"
                                ]
                            )
                    else:
                        if depencia not in keys:
                            list_errors.append(
                                [
                                    f"{key} -> {data['name']}: sem {depencia} - {dict_values[depencia]} Valido na lista!"
                                ]
                            )
                        else:

                            def valida(x, y):
                                return x["name"] == y

                            if type(dict_values[depencia]) == list:
                                for value in dict_values[depencia]:
                                    list_verification = list(
                                        map(
                                            lambda d: valida(d, value),
                                            list_objects[depencia],
                                        )
                                    )
                                    if (
                                        True in list_verification
                                        or value in DICT_EXCLUDE
                                    ):
                                        continue
                                    else:
                                        list_errors.append(
                                            [
                                                f"{key} -> {data['name']}: sem {depencia} - {value} adicionado a lista!"
                                            ]
                                        )
                            else:
                                list_verification = list(
                                    map(
                                        lambda d: valida(d, dict_values[depencia]),
                                        list_objects[depencia],
                                    )
                                )
                                if True in list_verification:
                                    continue
                                else:
                                    list_errors.append(
                                        [
                                            f"{key} -> {data['name']}: sem {depencia} - {dict_values[depencia]} adicionado a lista!"
                                        ]
                                    )

        return list_errors
