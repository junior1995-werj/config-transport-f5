from flask import render_template

from handler.big_ip.big_ip import TransportConfig
from handler.ltm.generic_message.generic_message import GenenricMessage


def peer(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GenenricMessage()
    peers = query.get_peer_by_id(id)
    return render_template(
        "ltm/generic_message/peer.html", peers=peers, id=id, configs=configs
    )


def protocol(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GenenricMessage()
    protocols = query.get_protocol_by_id(id)
    return render_template(
        "ltm/generic_message/protocol.html", protocols=protocols, id=id, configs=configs
    )


def route(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GenenricMessage()
    routes = query.get_route_by_id(id)
    return render_template(
        "ltm/generic_message/route.html", routes=routes, id=id, configs=configs
    )


def router(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GenenricMessage()
    routers = query.get_router_by_id(id)
    return render_template(
        "ltm/generic_message/router.html", routers=routers, id=id, configs=configs
    )


def transport_config(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GenenricMessage()
    transport_configs = query.get_transport_config_by_id(id)
    return render_template(
        "ltm/generic_message/transport_config.html",
        transport_configs=transport_configs,
        id=id,
        configs=configs,
    )
