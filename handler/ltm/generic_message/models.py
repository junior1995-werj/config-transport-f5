from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PeerModel(Base):
    __tablename__ = "big_ip_message_routing_peer"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    pool = Column(String())
    transport_name = Column(String())
    auto_initialization = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        name,
        pool,
        transport_name,
        auto_initialization,
        partition_id,
        comand,
        external_id,
    ):
        self.name = name
        self.pool = pool
        self.transport_name = transport_name
        self.auto_initialization = auto_initialization
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class ProtocolModel(Base):
    __tablename__ = "big_ip_message_routing_protocol"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    disable_parser = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, disable_parser, partition_id, comand, external_id):
        self.name = name
        self.disable_parser = disable_parser
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class RouteModel(Base):
    __tablename__ = "big_ip_message_routing_route"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    peer = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, peer, partition_id, comand, external_id):
        self.name = name
        self.peer = peer
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class RouterModel(Base):
    __tablename__ = "big_ip_message_routing_router"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    route = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, route, partition_id, comand, external_id):
        self.name = name
        self.route = route
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id


class GmTransportConfigModel(Base):
    __tablename__ = "big_ip_message_routing_transport_config"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    rule = Column(String())
    profiles = Column(String())
    partition_id = Column(String())
    comand = Column(String())
    external_id = Column(String())

    def __init__(self, name, rule, profiles, partition_id, comand, external_id):
        self.name = name
        self.rule = rule
        self.profiles = profiles
        self.partition_id = partition_id
        self.comand = comand
        self.external_id = external_id
