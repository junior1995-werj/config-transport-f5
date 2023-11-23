from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VlansModel(Base):
    __tablename__ = "big_ip_network_vlans"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    tag = Column(String())
    interfaces = Column(String())
    mtu = Column(String())
    failsafe_enabled = Column(String())
    auto_lasthop = Column(String())
    description = Column(String())
    mac = Column(String())
    comand = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self,
        name,
        tag,
        interfaces,
        mtu,
        failsafe_enabled,
        auto_lasthop,
        description,
        mac,
        comand,
        external_id,
    ):
        self.name = name
        self.tag = tag
        self.interfaces = interfaces
        self.mtu = mtu
        self.failsafe_enabled = failsafe_enabled
        self.auto_lasthop = auto_lasthop
        self.description = description
        self.mac = mac
        self.comand = comand
        self.external_id = external_id


class TrunkModel(Base):
    __tablename__ = "big_ip_network_trunk"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    cfg_mbr_count = Column(String())
    bandwidth = Column(String())
    interfaces = Column(String())
    link_select_policy = Column(String())
    mac_address = Column(String())
    lacp_enabled = Column(String())
    comand = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self,
        name,
        cfg_mbr_count,
        bandwidth,
        interfaces,
        link_select_policy,
        mac_address,
        lacp_enabled,
        comand,
        external_id,
    ):
        self.name = name
        self.cfg_mbr_count = cfg_mbr_count
        self.bandwidth = bandwidth
        self.interfaces = interfaces
        self.link_select_policy = link_select_policy
        self.mac_address = mac_address
        self.lacp_enabled = lacp_enabled
        self.comand = comand
        self.external_id = external_id


class SelfIpModel(Base):
    __tablename__ = "big_ip_network_self_ip"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    ip_addr = Column(String())
    net_mask = Column(String())
    vlan = Column(String())
    port_lock_down = Column(String())
    traffic_group = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self,
        name,
        ip_addr,
        netmask,
        vlan,
        port_lock_down,
        traffic_group,
        partition_id,
        comand,
        external_id,
    ):
        self.name = name
        self.ip_addr = ip_addr
        self.net_mask = netmask
        self.vlan = vlan
        self.port_lock_down = port_lock_down
        self.traffic_group = traffic_group
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class StaticRouteModel(Base):
    __tablename__ = "big_ip_network_static_route"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    destination = Column(String())
    netmask = Column(String())
    gateway = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self, name, destination, netmask, gateway, partition_id, comand, external_id
    ):
        self.name = name
        self.destination = destination
        self.netmask = netmask
        self.gateway = gateway
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class InterfaceModel(Base):
    __tablename__ = "big_ip_network_interface"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    vendor_name = Column(String())
    vendor_partnum = Column(String())
    serial_number = Column(String())
    mac_addr = Column(String())
    mtu = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        vendor_name,
        vendor_partnum,
        serial_number,
        mac_addr,
        mtu,
        comand,
        external_id,
    ):
        self.name = name
        self.vendor_name = vendor_name
        self.vendor_partnum = vendor_partnum
        self.serial_number = serial_number
        self.mac_addr = mac_addr
        self.mtu = mtu
        self.comand = comand
        self.external_id = external_id


class RoutesDomaninModel(Base):
    __tablename__ = "big_ip_network_route_domain"

    id = Column(Integer, primary_key=True, index=True)
    id_route = Column(String())
    name = Column(String())
    strick_isolation = Column(String())
    vlans = Column(String())
    dynamic_routing_protocols = Column(String())
    conn_limit = Column(String())
    partition_id = Column(String())
    route_default = Column(Boolean())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        id_route,
        name,
        strick_isolation,
        vlans,
        dynamic_routing_protocols,
        conn_limit,
        partition_id,
        route_default,
        comand,
        external_id,
    ):
        self.id_route = id_route
        self.name = name
        self.strick_isolation = strick_isolation
        self.vlans = vlans
        self.dynamic_routing_protocols = dynamic_routing_protocols
        self.conn_limit = conn_limit
        self.partition_id = partition_id
        self.route_default = route_default
        self.comand = comand
        self.external_id = external_id


class PacketFilterRulesModel(Base):
    __tablename__ = "big_ip_network_packet_filter_rule"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    expression = Column(String())
    action = Column(String())
    vname = Column(String())
    order_weight = Column(String())
    log = Column(String())
    partiton_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        expression,
        action,
        vname,
        order_weight,
        log,
        partiton_id,
        comand,
        external_id,
    ):
        self.name = name
        self.expression = expression
        self.action = action
        self.vname = vname
        self.order_weight = order_weight
        self.log = log
        self.partiton_id = partiton_id
        self.comand = comand
        self.external_id = external_id
