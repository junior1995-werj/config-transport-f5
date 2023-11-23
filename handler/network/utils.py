def encontrar_proximo_vazio(string, indice):
    tamanho = len(string)
    while indice < tamanho:
        if string[indice] == " ":
            return indice
        indice += 1
    return -1


def find_vlans(data: str):
    data = data.replace("net vlan ", "")
    data = data.split("\n")

    vlans_list = []
    for vlan in data:
        name = vlan[: vlan.find(" ")]
        tag = vlan[
            vlan.find(" tag ")
            + 5 : encontrar_proximo_vazio(vlan, vlan.find(" tag ") + 5)
        ]
        mtu = vlan[
            vlan.find("mtu") + 4 : encontrar_proximo_vazio(vlan, vlan.find("mtu") + 4)
        ]
        interfaces = vlan[
            vlan.find("interfaces")
            + 13 : vlan.find("} } ", vlan.find("interfaces") + 13)
        ]
        interfaces = interfaces.replace("{", "-")
        interfaces = interfaces.split(" } ")

        list_interface = []
        cont = 0
        while cont < len(interfaces):
            interface = interfaces[0].replace(" app-service none tag-mode none", "")
            list_interface.append(interface.replace(" ", ""))
            cont += 1

        vlans_list.append(
            {
                "name": name,
                "tag": tag,
                "mtu": mtu,
                "interfaces": list_interface,
            }
        )

    return vlans_list


def find_trunks(data: str):
    data = data.replace("net trunk ", "")
    data = data.split("\n")

    trunks_list = []
    for trunk in data:
        name = trunk[: trunk.find(" ")]
        if trunk.find("cfg-mbr-count") != -1:
            cfg_mbr_count = trunk[
                trunk.find("cfg-mbr-count")
                + 14 : encontrar_proximo_vazio(trunk, trunk.find("cfg-mbr-count") + 14)
            ]
        else:
            cfg_mbr_count = ""
        if trunk.find("bandwidth") != -1:
            bandwidth = trunk[
                trunk.find("bandwidth")
                + 10 : encontrar_proximo_vazio(trunk, trunk.find("bandwidth") + 10)
            ]
        else:
            bandwidth = ""
        if trunk.find("mac-address") != -1:
            mac_address = trunk[
                trunk.find("mac-address")
                + 12 : encontrar_proximo_vazio(trunk, trunk.find("mac-address") + 12)
            ]
        else:
            mac_address = ""
        if trunk.find("link-select-policy") != -1:
            link_select_policy = trunk[
                trunk.find("link-select-policy")
                + 19 : encontrar_proximo_vazio(
                    trunk, trunk.find("link-select-policy") + 19
                )
            ]
        else:
            link_select_policy = ""
        if trunk.find("media") != -1:
            media = trunk[
                trunk.find("media")
                + 6 : encontrar_proximo_vazio(trunk, trunk.find("media") + 6)
            ]
        else:
            media = ""
        if trunk.find("working-mbr-count") != -1:
            working_mbr_count = trunk[
                trunk.find("working-mbr-count")
                + 18 : encontrar_proximo_vazio(
                    trunk, trunk.find("working-mbr-count") + 18
                )
            ]
        else:
            working_mbr_count = ""
        interfaces = trunk[trunk.find("interfaces ") : trunk.find("}") + 1]
        interfaces = (
            interfaces.replace("interfaces ", "").replace("{", "").replace("}", "")
        )
        interfaces = interfaces.split(" ")
        interfaces = list(filter(bool, interfaces))

        trunks_list.append(
            {
                "name": name,
                "cfg_mbr_count": cfg_mbr_count,
                "bandwidth": bandwidth,
                "mac_address": mac_address,
                "link_select_policy": link_select_policy,
                "media": media,
                "working_mbr_count": working_mbr_count,
                "interfaces": interfaces,
            }
        )

    return trunks_list


def find_static_routes(data: str):
    if not data:
        return data
    data = data.replace("net route ", "")
    data = data.split("\n")

    static_routes_list = []
    for sr in data:

        name = sr[: sr.find(" ")]
        if sr.find("network") != -1:
            destination = sr[
                sr.find("network")
                + 8 : encontrar_proximo_vazio(sr, sr.find("network") + 8)
            ]
        else:
            destination = ""
        if sr.find("gw") != -1:
            nexthop = sr[
                sr.find("gw") + 3 : encontrar_proximo_vazio(sr, sr.find("gw") + 3)
            ]
        else:
            nexthop = ""

        static_routes_list.append(
            {
                "name": name,
                "destination": destination,
                "nexthop": nexthop,
            }
        )

    return static_routes_list


def find_self_ip(data: str):
    if not data:
        return data
    data = data.replace("net self ", "")
    data = data.split("\n")

    self_ip_list = []

    for self_ip in data:
        name = self_ip[: self_ip.find(" ")]
        if self_ip.find("address") != -1:
            ip_addr = self_ip[
                self_ip.find("address")
                + 8 : encontrar_proximo_vazio(self_ip, self_ip.find("address") + 8)
            ]
            ip_addr = ip_addr.split("/")
            net_mask = ip_addr[1]
            ip_addr = ip_addr[0]
        else:
            ip_addr = ""
        if self_ip.find("vlan") != -1:
            vlan = self_ip[
                self_ip.find("vlan")
                + 5 : encontrar_proximo_vazio(self_ip, self_ip.find("vlan") + 5)
            ]
        else:
            vlan = ""
        if self_ip.find(" traffic-group ") != -1:
            trafic_group = self_ip[
                self_ip.find(" traffic-group ")
                + 15 : encontrar_proximo_vazio(
                    self_ip, self_ip.find(" traffic-group ") + 15
                )
            ]
        else:
            trafic_group = ""

        if (
            self_ip[
                self_ip.find("allow-service")
                + 14 : encontrar_proximo_vazio(
                    self_ip, self_ip.find("allow-service") + 14
                )
            ]
            == "all"
        ):
            port_lock_down = self_ip[
                self_ip.find("allow-service")
                + 14 : encontrar_proximo_vazio(
                    self_ip, self_ip.find("allow-service") + 14
                )
            ]
        else:
            port_lock_down = self_ip[
                self_ip.find("allow-service") : self_ip.find(
                    "}", self_ip.find("allow-service")
                )
            ]
            port_lock_down = port_lock_down.replace("allow-service ", "").replace(
                "{", ""
            )
            port_lock_down = port_lock_down.split(" ")
            port_lock_down = list(filter(bool, port_lock_down))

        self_ip_list.append(
            {
                "name": name,
                "ip_addr": ip_addr,
                "net_mask": net_mask,
                "vlan": vlan,
                "trafic_group": trafic_group,
                "port_lock_down": str(port_lock_down),
            }
        )

    return self_ip_list
