from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PoolModel(Base):
    __tablename__ = "big_ip_ltm_pool"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    description = Column(String())
    members = Column(String())
    loadBalancingMode = Column(String())
    monitor = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        description,
        members,
        loadBalancingMode,
        monitor,
        external_id,
        partition_id,
        comand,
        id=None,
    ):
        self.name = name
        self.description = description
        self.members = members
        self.loadBalancingMode = loadBalancingMode
        self.monitor = monitor
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class VirtualServersModel(Base):
    __tablename__ = "big_ip_ltm_virtual_server"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    description = Column(String())
    destination = Column(String())
    type = Column(String())
    port = Column(String())
    mask = Column(String())
    source = Column(String())
    ip_proto = Column(String())
    source_address_translation_type = Column(String())
    translate_addr = Column(String())
    translate_port = Column(String())
    rulesReference = Column(String())
    pool = Column(String())
    profilesReference = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self,
        name,
        description,
        destination,
        type,
        port,
        mask,
        source,
        ip_proto,
        source_address_translation_type,
        translate_addr,
        translate_port,
        rulesReference,
        pool,
        profilesReference,
        partition_id,
        comand,
        external_id,
    ):
        self.name = name
        self.description = description
        self.destination = destination
        self.type = type
        self.port = port
        self.mask = mask
        self.source = source
        self.ip_proto = ip_proto
        self.source_address_translation_type = source_address_translation_type
        self.translate_addr = translate_addr
        self.translate_port = translate_port
        self.rulesReference = rulesReference
        self.pool = pool
        self.profilesReference = profilesReference
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class iRuleModel(Base):
    __tablename__ = "big_ip_ltm_irule"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    definition = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        definition,
        partition_id,
        comand,
        external_id,
        _sa_instance_state=None,
    ):
        self.name = name
        self.definition = definition
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class DataGroupModel(Base):
    __tablename__ = "big_ip_ltm_datagroup"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    data_type = Column(String())
    records = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        data_type,
        records,
        partition_id,
        comand,
        external_id,
        _sa_instance_state=None,
    ):
        self.name = name
        self.data_type = data_type
        self.records = records
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class MonitorModel(Base):
    __tablename__ = "big_ip_ltm_monitor"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    interval = Column(String())
    timeout = Column(String())
    send = Column(String())
    recv = Column(String())
    defaultsFrom = Column(String())
    destination = Column(String())
    port = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        interval,
        timeout,
        defaultsFrom,
        destination,
        port,
        partition_id,
        comand,
        external_id,
        send=None,
        recv=None,
        _sa_instance_state=None,
    ):
        self.name = name
        self.interval = interval
        self.timeout = timeout
        self.send = send
        self.recv = recv
        self.defaultsFrom = defaultsFrom
        self.destination = destination
        self.port = port
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class SnatModel(Base):
    __tablename__ = "big_ip_ltm_snat"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    description = Column(String())
    trans_addr_name = Column(String())
    origins = Column(String())
    srcport = Column(String())
    vlans = Column(String())
    auto_lasthop = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        description,
        trans_addr_name,
        origins,
        vlans,
        partition_id,
        comand,
        external_id,
        auto_lasthop=None,
        srcport=None,
        _sa_instance_state=None,
    ):
        self.name = name
        self.description = description
        self.trans_addr_name = trans_addr_name
        self.origins = origins
        self.srcport = srcport
        self.vlans = vlans
        self.auto_lasthop = auto_lasthop
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class SnatpoolModel(Base):
    __tablename__ = "big_ip_ltm_snat_pool"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    members = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self, name, members, partition_id, comand, external_id, _sa_instance_state=None
    ):
        self.name = name
        self.members = members
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class NatModel(Base):
    __tablename__ = "big_ip_ltm_nat"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    trans_addr = Column(String())
    orig_addr = Column(String())
    traffic_group = Column(String())
    vlans = Column(String())
    auto_lasthop = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        trans_addr,
        orig_addr,
        traffic_group,
        vlans,
        auto_lasthop,
        partition_id,
        comand,
        external_id,
        _sa_instance_state=None,
    ):
        self.name = name
        self.trans_addr = trans_addr
        self.orig_addr = orig_addr
        self.traffic_group = traffic_group
        self.vlans = vlans
        self.auto_lasthop = auto_lasthop
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class ProfilesSSLModel(Base):
    __tablename__ = "big_ip_ltm_profiles_ssl"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    default_name = Column(String())
    ciphers = Column(String())
    cert = Column(String())
    partition_id = Column(String())
    service = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        default_name,
        ciphers,
        cert,
        partition_id,
        service,
        comand,
        external_id,
        _sa_instance_state=None,
    ):
        self.name = name
        self.default_name = default_name
        self.ciphers = ciphers
        self.cert = cert
        self.partition_id = partition_id
        self.service = service
        self.comand = comand
        self.external_id = external_id


class ProfilesServicesModel(Base):
    __tablename__ = "big_ip_ltm_profiles_services"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    default_name = Column(String())
    partition_id = Column(String())
    service = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, default_name, partition_id, service, comand, external_id):
        self.name = name
        self.default_name = default_name
        self.partition_id = partition_id
        self.service = service
        self.comand = comand
        self.external_id = external_id


class ProfilesPersistModel(Base):
    __tablename__ = "big_ip_ltm_profiles_persist"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    default_name = Column(String())
    partition_id = Column(String())
    service = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, default_name, partition_id, service, comand, external_id):
        self.name = name
        self.default_name = default_name
        self.partition_id = partition_id
        self.service = service
        self.comand = comand
        self.external_id = external_id


class ProfilesProtocolModel(Base):
    __tablename__ = "big_ip_ltm_profiles_protocol"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    default_name = Column(String())
    partition_id = Column(String())
    service = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, default_name, partition_id, service, comand, external_id):
        self.name = name
        self.default_name = default_name
        self.partition_id = partition_id
        self.service = service
        self.comand = comand
        self.external_id = external_id


class ProfilesOtherModel(Base):
    __tablename__ = "big_ip_ltm_profiles_others"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    default_name = Column(String())
    partition_id = Column(String())
    service = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, default_name, partition_id, service, comand, external_id):
        self.name = name
        self.default_name = default_name
        self.partition_id = partition_id
        self.service = service
        self.comand = comand
        self.external_id = external_id


class PoliciesModel(Base):
    __tablename__ = "big_ip_ltm_policies"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    status = Column(String())
    strategy = Column(String())
    last_modified = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        status,
        last_modified,
        strategy,
        partition_id,
        comand,
        external_id,
        _sa_instance_state=None,
    ):
        self.name = name
        self.status = status
        self.last_modified = last_modified
        self.strategy = strategy
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id
