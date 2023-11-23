from flask import render_template
from flask_login import current_user, login_required

from config import settings
from handler.gtm.gtm import GTM
from handler.big_ip.big_ip import TransportConfig


@login_required
def datacenter(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GTM()
    datacenters = query.get_static_datacenter_by_id(id)
    return render_template(
        "gtm/datacenter.html",
        datacenters=datacenters,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def server_gtm(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GTM()
    servers_gtm = query.get_static_server_gtm_by_id(id)
    return render_template(
        "gtm/server_gtm.html",
        servers_gtm=servers_gtm,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def server_ip(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GTM()
    server_ips = query.get_static_server_ip_by_id(id)
    return render_template(
        "gtm/server_ip.html",
        server_ips=server_ips,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def wide_ip(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GTM()
    wide_ips = query.get_static_wide_ip_by_id(id)
    return render_template(
        "gtm/wide_ip.html",
        wide_ips=wide_ips,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def pool_wide_ip(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = GTM()
    pool_wide_ips = query.get_static_pool_wide_ip_by_id(id)
    return render_template(
        "gtm/pool_wide_ip.html",
        pool_wide_ips=pool_wide_ips,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )
