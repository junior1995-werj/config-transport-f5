from netmiko import ConnectHandler
from sqlalchemy.orm import sessionmaker

from handler.gtm.models import (
    WideIpModel,
    ServerIpModel,
    ServerGtmModel,
    DatacenterModel,
    PoolWideIpModel,
)
from handler.utils.utils import UtilsUtils
from handler.database.connect_db import engine

utils = UtilsUtils()


class GTM:
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

    def create_register_database_datacenter(self):
        sessao = self.session()
        root_key = "gtm_dc"
        child_keys_list = ["leaf_name", "location"]
        datacenters = utils.json_parser(self.file, root_key, child_keys_list)

        if datacenters:
            for data in datacenters:
                sessao.add(DatacenterModel(**data, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_static_datacenter_by_id(self, external_id):
        sessao = self.session()
        datacenters = (
            sessao.query(DatacenterModel)
            .filter(DatacenterModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datacenters = []

        for datacenter in datacenters:
            list_datacenters.append(
                {
                    "id": datacenter.id,
                    "name": datacenter.name,
                    "location": datacenter.location,
                    "external_id": datacenter.external_id,
                }
            )
        return list_datacenters

    def create_register_database_server_gtm(self):
        sessao = self.session()
        root_key = "gtm_server"
        child_keys_list = ["description", "leaf_name", "dc_name"]
        servers_gtm = utils.json_parser(self.file, root_key, child_keys_list)

        if servers_gtm:
            for data in servers_gtm:
                sessao.add(ServerGtmModel(**data, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_static_server_gtm_by_id(self, external_id):
        sessao = self.session()
        datacenters = (
            sessao.query(ServerGtmModel)
            .filter(ServerGtmModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datacenters = []

        for datacenter in datacenters:
            list_datacenters.append(
                {
                    "id": datacenter.id,
                    "name": datacenter.name,
                    "description": datacenter.description,
                    "dc_name": datacenter.dc_name,
                    "external_id": datacenter.external_id,
                }
            )
        return list_datacenters

    def create_register_database_server_ip(self):
        sessao = self.session()
        root_key = "gtm_device_ip"
        child_keys_list = [
            "description",
            "device_name",
            "server_name",
            "ip",
            "assigned_link_name",
        ]
        server_ips = utils.json_parser(self.file, root_key, child_keys_list)

        if server_ips:
            for data in server_ips:
                sessao.add(ServerIpModel(**data, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_static_server_ip_by_id(self, external_id):
        sessao = self.session()
        datacenters = (
            sessao.query(ServerIpModel)
            .filter(ServerIpModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datacenters = []

        for datacenter in datacenters:
            list_datacenters.append(
                {
                    "id": datacenter.id,
                    "name": datacenter.name,
                    "description": datacenter.description,
                    "device_name": datacenter.device_name,
                    "ip": datacenter.ip,
                    "assigned_link_name": datacenter.assigned_link_name,
                    "external_id": datacenter.external_id,
                }
            )
        return list_datacenters

    def create_register_database_wide_ip(self):
        sessao = self.session()
        root_key = "gtm_wideip_pool"
        child_keys_list = [
            "partition_id",
            "wip_name",
            "pool_name",
            "wip_type",
            "pool_type",
            "wip_pool_order",
        ]
        wide_ips = utils.json_parser(self.file, root_key, child_keys_list)

        if wide_ips:
            for data in wide_ips:
                sessao.add(WideIpModel(**data, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_static_wide_ip_by_id(self, external_id):
        sessao = self.session()
        datacenters = (
            sessao.query(WideIpModel)
            .filter(WideIpModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datacenters = []

        for datacenter in datacenters:
            list_datacenters.append(
                {
                    "id": datacenter.id,
                    "name": datacenter.name,
                    "partition_id": datacenter.partition_id,
                    "pool_name": datacenter.pool_name,
                    "wip_type": datacenter.wip_type,
                    "pool_type": datacenter.pool_type,
                    "wip_pool_order": datacenter.wip_pool_order,
                    "external_id": datacenter.external_id,
                }
            )
        return list_datacenters

    def create_register_database_pool_wide_ip(self):
        sessao = self.session()
        root_key = "gtm_pool_member"
        child_keys_list = [
            "description",
            "partition_id",
            "pool_name",
            "pool_type",
            "vs_name",
        ]
        pool_wide_ips = utils.json_parser(self.file, root_key, child_keys_list)

        if pool_wide_ips:
            for data in pool_wide_ips:
                sessao.add(PoolWideIpModel(**data, external_id=self.external_id))

        sessao.commit()
        sessao.close()

    def get_static_pool_wide_ip_by_id(self, external_id):
        sessao = self.session()
        datacenters = (
            sessao.query(PoolWideIpModel)
            .filter(PoolWideIpModel.external_id == str(external_id))
            .all()
        )
        sessao.close()
        list_datacenters = []

        for datacenter in datacenters:
            list_datacenters.append(
                {
                    "id": datacenter.id,
                    "description": datacenter.description,
                    "partition_id": datacenter.partition_id,
                    "pool_name": datacenter.pool_name,
                    "pool_type": datacenter.pool_type,
                    "vs_name": datacenter.vs_name,
                    "external_id": datacenter.external_id,
                }
            )
        return list_datacenters
