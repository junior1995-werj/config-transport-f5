from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SystemInformationModel(Base):
    __tablename__ = "big_ip_system_system_information"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String())
    host_board_serial_num = Column(String())
    bigip_chassis_serial_num = Column(String())
    external_id = Column(String())

    def __init__(
        self, platform, host_board_serial_num, bigip_chassis_serial_num, external_id
    ):
        self.platform = platform
        self.host_board_serial_num = host_board_serial_num
        self.bigip_chassis_serial_num = bigip_chassis_serial_num
        self.external_id = external_id


class DevicegroupModel(Base):
    __tablename__ = "big_ip_system_devicegroup"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    network_failover_enabled = Column(String())
    autosync_enabled = Column(String())
    external_id = Column(String())

    def __init__(self, name, network_failover_enabled, autosync_enabled, external_id):
        self.name = name
        self.network_failover_enabled = network_failover_enabled
        self.autosync_enabled = autosync_enabled
        self.external_id = external_id


class FolderModel(Base):
    __tablename__ = "big_ip_system_folder"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    devicegroup = Column(String())
    traffic_group = Column(String())
    external_id = Column(String())

    def __init__(self, leaf_name, devicegroup, traffic_group, external_id):
        self.name = leaf_name
        self.devicegroup = devicegroup
        self.traffic_group = traffic_group
        self.external_id = external_id


class SystemModuleModel(Base):
    __tablename__ = "big_ip_system_system_module"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    provision_level = Column(String())
    licensed = Column(String())
    expiration_date = Column(String())
    external_id = Column(String())

    def __init__(
        self, display_name, provision_level, licensed, expiration_date, external_id
    ):
        self.name = display_name
        self.provision_level = provision_level
        self.licensed = licensed
        self.expiration_date = expiration_date
        self.external_id = external_id


class SysDeviceModel(Base):
    __tablename__ = "big_ip_system_sys_device"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String())
    chassis_id = Column(String())
    mgmt_ip = Column(String())
    configsync_ip = Column(String())
    failover_state = Column(String())
    version = Column(String())
    edition = Column(String())
    build = Column(String())
    timezone = Column(String())
    external_id = Column(String())

    def __init__(
        self,
        hostname,
        chassis_id,
        mgmt_ip,
        configsync_ip,
        failover_state,
        version,
        edition,
        build,
        timezone,
        external_id,
    ):
        self.hostname = hostname
        self.chassis_id = chassis_id
        self.mgmt_ip = mgmt_ip
        self.configsync_ip = configsync_ip
        self.failover_state = failover_state
        self.version = version
        self.edition = edition
        self.build = build
        self.timezone = timezone
        self.external_id = external_id


class ChassisModel(Base):
    __tablename__ = "big_ip_system_chassis"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    serial_num = Column(String())
    reg_key = Column(String())
    external_id = Column(String())

    def __init__(self, marketing_name, serial_num, reg_key, external_id):
        self.name = marketing_name
        self.serial_num = serial_num
        self.reg_key = reg_key
        self.external_id = external_id


class iCallModel(Base):
    __tablename__ = "big_ip_system_icall"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    definition = Column(String())
    type_icall = Column(String())
    external_id = Column(String())

    def __init__(self, name, definition, type_icall, external_id):
        self.name = name
        self.definition = definition
        self.type_icall = type_icall
        self.external_id = external_id


class TrafficGroupModel(Base):
    __tablename__ = "big_ip_system_trafic_group"

    id = Column(Integer, primary_key=True, index=True)
    partition_id = Column(String())
    name = Column(String())
    failover_method = Column(String())
    external_id = Column(String())

    def __init__(self, partition_id, name, failover_method, external_id):
        self.partition_id = partition_id
        self.name = name
        self.failover_method = failover_method
        self.external_id = external_id


class UserModel(Base):
    __tablename__ = "big_ip_system_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    description = Column(String())
    role = Column(String())
    limit_session = Column(String())
    external_id = Column(String())

    def __init__(self, name, description, role, limit_session, external_id):
        self.name = name
        self.description = description
        self.role = role
        self.limit_session = limit_session
        self.external_id = external_id


class UserAlertModel(Base):
    __tablename__ = "big_ip_system_user_alert"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    user_alert = Column(String())
    external_id = Column(String())

    def __init__(self, name, user_alert, external_id):
        self.name = name
        self.user_alert = user_alert
        self.external_id = external_id
