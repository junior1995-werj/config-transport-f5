from flask import render_template
from flask_login import current_user, login_required

from config import settings
from handler.ltm.ltm import Ltm
from handler.big_ip.big_ip import TransportConfig


@login_required
def pool(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    data = query.get_pool_by_id(id)
    return render_template(
        "ltm/pool.html",
        data=data,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def virtual_server(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    data = query.get_virtual_server_by_id(id)
    return render_template(
        "ltm/virtual_server.html",
        data=data,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def datagroup(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    datagroups = query.get_datagroup_by_id(id)
    return render_template(
        "ltm/datagroup.html",
        datagroups=datagroups,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def irule(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    irules = query.get_irule_by_id(id)
    return render_template(
        "ltm/irule.html",
        irules=irules,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def monitor(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    monitors = query.get_monitor_by_id(id)
    return render_template(
        "ltm/monitor.html",
        monitors=monitors,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def profiles(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    (
        profiles_ssl,
        profiles_services,
        profiles_persist,
        profiles_protocol,
        profiles_other,
    ) = query.get_profiles_by_id(id)
    return render_template(
        "ltm/profiles.html",
        profiles_ssl=profiles_ssl,
        profiles_services=profiles_services,
        profiles_persist=profiles_persist,
        profiles_protocol=profiles_protocol,
        profiles_other=profiles_other,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def policies(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    policies = query.get_policies_by_id(id)
    return render_template(
        "ltm/policies.html",
        policies=policies,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def snat(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    snats = query.get_snat_by_id(id)
    return render_template(
        "ltm/snat.html",
        snats=snats,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def snat_pool(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    snatpools = query.get_snat_pool_by_id(id)
    return render_template(
        "ltm/snat_pool.html",
        snatpools=snatpools,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def nat(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = Ltm()
    nats = query.get_nat_by_id(id)
    return render_template(
        "ltm/nat.html",
        nats=nats,
        id=id,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )
