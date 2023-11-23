import time

from handler.gtm.models import DatacenterModel
from handler.ltm.models import PoolModel
from handler.user.models import UserModel
from handler.big_ip.big_ip import BigIpQkView
from handler.big_ip.models import BigIpModel
from handler.system.models import SystemInformationModel
from handler.network.models import SelfIpModel
from handler.database.connect_db import engine
from handler.ltm.generic_message.models import PeerModel

# SystemInformationModel.metadata.drop_all(engine)
# PoolModel.metadata.drop_all(engine)
# SelfIpModel.metadata.drop_all(engine)
# BigIpModel.metadata.drop_all(engine)
# DatacenterModel.metadata.drop_all(engine)
# PeerModel.metadata.drop_all(engine)
# UserModel.metadata.drop_all(engine)
time.sleep(2)
SystemInformationModel.metadata.create_all(engine)
PoolModel.metadata.create_all(engine)
SelfIpModel.metadata.create_all(engine)
BigIpModel.metadata.create_all(engine)
DatacenterModel.metadata.create_all(engine)
PeerModel.metadata.create_all(engine)
UserModel.metadata.create_all(engine)


net = BigIpQkView(file="support_san.qkview")

net.process_file()
