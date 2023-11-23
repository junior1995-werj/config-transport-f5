from flask import render_template
from flask_login import current_user, login_required

from config import settings
from handler.big_ip.big_ip import TransportConfig
from handler.network.network import Network


@login_required
def vlans(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    vlans = query.get_vlans_by_id(id)
    return render_template(
        "network/vlans.html",
        vlans=vlans,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def trunks(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    trunks = query.get_trunks_by_id(id)
    return render_template(
        "network/trunks.html",
        trunks=trunks,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def self_ip(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    self_ips = query.get_self_ip_by_id(id)
    return render_template(
        "network/self_ip.html",
        self_ips=self_ips,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def routes_statics(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    static_routes = query.get_static_route_by_id(id)
    return render_template(
        "network/routes_statics.html",
        static_routes=static_routes,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def interfaces(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    interfaces = query.get_interface_by_id(id)
    return render_template(
        "network/interfaces.html",
        interfaces=interfaces,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def routes_domains(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    routes_domains = query.get_routes_domains_by_id(id)
    return render_template(
        "network/routes_domains.html",
        routes_domains=routes_domains,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def packet_filters_rule(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Network()
    packet_filters_rules = query.get_packet_filters_rule_by_id(id)
    return render_template(
        "network/packet_filters_rule.html",
        packet_filters_rules=packet_filters_rules,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )
