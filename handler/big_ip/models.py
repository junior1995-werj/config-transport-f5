import uuid

from sqlalchemy import UUID, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BigIpModel(Base):
    __tablename__ = "big_ip_big_ip"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    host = Column(String())
    username = Column(String())
    password = Column(String())
    status = Column(Boolean())
    date_conection = Column(DateTime())
    version = Column(String())
    hostname = Column(String())
    ntp_servers = Column(String())
    ntp_timezone = Column(String())
    dns_name_servers = Column(String())
    dns_search = Column(String())
    ip_management = Column(String())
    gateway = Column(String())
    snmp_contact = Column(String())
    snmp_location = Column(String())
    snmp_allowed = Column(String())
    bigip_chassis_serial_num = Column(String())
    user_import = Column(String())

    def __init__(
        self,
        id,
        host,
        username,
        password,
        status,
        date_conection,
        user_import,
        version=None,
        hostname=None,
        ntp_servers=None,
        ntp_timezone=None,
        dns_name_servers=None,
        dns_search=None,
        ip_management=None,
        gateway=None,
        snmp_contact=None,
        snmp_location=None,
        snmp_allowed=None,
        bigip_chassis_serial_num=None,
    ):
        self.id = id
        self.host = host
        self.username = username
        self.password = password
        self.status = status
        self.date_conection = date_conection
        self.version = version
        self.hostname = hostname
        self.ntp_servers = ntp_servers
        self.ntp_timezone = ntp_timezone
        self.dns_name_servers = dns_name_servers
        self.dns_search = dns_search
        self.ip_management = ip_management
        self.gateway = gateway
        self.snmp_contact = snmp_contact
        self.snmp_location = snmp_location
        self.snmp_allowed = snmp_allowed
        self.bigip_chassis_serial_num = bigip_chassis_serial_num
        self.user_import = user_import


class TransportConfigModel(Base):
    __tablename__ = "big_ip_big_ip_transport_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    internal_id = Column(String())
    service = Column(String())
    external_id = Column(String(), index=True)
    data = Column(String())
    imported_configuration = Column(Boolean())

    def __init__(
        self,
        id,
        internal_id,
        service,
        external_id,
        data,
        imported_configuration,
        _sa_instance_state=None,
    ):
        self.id = id
        self.internal_id = internal_id
        self.service = service
        self.external_id = external_id
        self.data = data
        self.imported_configuration = imported_configuration


class TansportConfigImportModel(Base):
    __tablename__ = "big_ip_big_ip_transport_config_import"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    internal_id = Column(String())
    external_id = Column(String(), index=True)
    status = Column(String())
    reason = Column(String())
    service = Column(String())
    data = Column(String())
    date_import = Column(DateTime())
    username = Column(String())

    def __init__(
        self,
        internal_id,
        external_id,
        status,
        reason,
        service,
        data,
        date_import,
        username,
    ):
        self.internal_id = internal_id
        self.external_id = external_id
        self.status = status
        self.reason = reason
        self.service = service
        self.data = data
        self.date_import = date_import
        self.username = username
