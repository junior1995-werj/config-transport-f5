from time import sleep

from flask_login import current_user
from flask_socketio import emit

from handler.big_ip.big_ip import (
    BigIpQkView,
    BigIpProcess,
    TransportConfig,
    TansportConfigImport,
)


def event_delete_connection(message):
    query = BigIpProcess()
    query.delete_connection(message["id"])


def event_add_all_config_default(message):
    transport_config = TransportConfig()
    transport_config.insert_all(
        external_id=message["external_id"], service=message["service"]
    )


def event_add_config_default(message):
    transport_config = TransportConfig()
    transport_config.insert_default_config(message=message)


def event_remove_config(message):
    transport_config = TransportConfig()
    transport_config.delete(
        external_id=message["external_id"],
        internal_id=message["internal_id"],
        id=message["id"],
    )


def event_remove_config_finish(message):
    transport_config = TransportConfig()
    transport_config.delete(
        external_id=message["external_id"],
        internal_id=message["internal_id"],
        service=message["service"],
    )


def event_update_config(message):
    transport_config = TransportConfig()
    transport_config.update(data=message)


def connect(message):
    emit("connect", {"data": "Connected", "count": 0})


def connecting(message):
    sleep(2)
    emit("init_migration", {"data": "Connected", "count": 0})


def event_add_config(message):
    transport_config = TransportConfig()
    transport_config.insert(
        external_id=message["external_id"],
        internal_id=message["internal_id"],
        service=message["service"],
    )


def send_services_new_big_ip(message):
    migrate = TansportConfigImport(
        external_id=message["external_id"],
        host=message["host"],
        username=message["username"],
        password=message["password"],
        user_migrate=current_user.username,
    )
    migrate.start()


def event_add_config_by_filter(message):
    transport_config = TransportConfig()
    transport_config.insert_by_filter(message)


def server_event(message):
    qkview = BigIpQkView(message["filename"], message["username"])
    qkview.process_file()
