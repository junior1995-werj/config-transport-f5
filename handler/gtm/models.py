from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatacenterModel(Base):
    __tablename__ = "big_ip_gtm_datacenter"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    location = Column(String())
    external_id = Column(String(), index=True)

    def __init__(self, leaf_name, location, external_id):
        self.name = leaf_name
        self.location = location
        self.external_id = external_id


class ServerGtmModel(Base):
    __tablename__ = "big_ip_gtm_server_gtm"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    description = Column(String())
    dc_name = Column(String())
    external_id = Column(String(), index=True)

    def __init__(self, leaf_name, description, dc_name, external_id):
        self.name = leaf_name
        self.description = description
        self.dc_name = dc_name
        self.external_id = external_id


class ServerIpModel(Base):
    __tablename__ = "big_ip_gtm_server_ip"

    id = Column(Integer, primary_key=True)
    description = Column(String())
    device_name = Column(String())
    name = Column(String())
    ip = Column(String())
    assigned_link_name = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self, description, device_name, server_name, ip, assigned_link_name, external_id
    ):
        self.description = description
        self.device_name = device_name
        self.name = server_name
        self.ip = ip
        self.assigned_link_name = assigned_link_name
        self.external_id = external_id


class WideIpModel(Base):
    __tablename__ = "big_ip_gtm_wide_ip"

    id = Column(Integer, primary_key=True)
    partition_id = Column(String())
    name = Column(String())
    pool_name = Column(String())
    wip_type = Column(String())
    pool_type = Column(String())
    wip_pool_order = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self,
        partition_id,
        name,
        pool_name,
        wip_type,
        pool_type,
        wip_pool_order,
        external_id,
    ):
        self.partition_id = partition_id
        self.name = name
        self.pool_name = pool_name
        self.wip_type = wip_type
        self.pool_type = pool_type
        self.wip_pool_order = wip_pool_order
        self.external_id = external_id


class PoolWideIpModel(Base):
    __tablename__ = "big_ip_gtm_pool_wide_ip"

    id = Column(Integer, primary_key=True)
    description = Column(String())
    partition_id = Column(String())
    pool_name = Column(String())
    pool_type = Column(String())
    vs_name = Column(String())
    external_id = Column(String(), index=True)

    def __init__(
        self, description, partition_id, pool_name, pool_type, vs_name, external_id
    ):
        self.description = description
        self.partition_id = partition_id
        self.pool_name = pool_name
        self.pool_type = pool_type
        self.vs_name = vs_name
        self.external_id = external_id
