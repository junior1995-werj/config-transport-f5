from flask import render_template
from flask_login import current_user, login_required

from config import settings
from handler.big_ip.big_ip import BigIpProcess, TransportConfig, TansportConfigComands


@login_required
def bigip(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = BigIpProcess()
    data = query.get_connection_by_id(id)
    return render_template(
        "index-big-ip.html",
        id=id,
        data=data,
        configs=configs,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def finalizar(id):
    comands = TansportConfigComands(external_id=id)
    list_comands = comands.start()
    transport_config = TransportConfig()
    configs, errors = transport_config.get_finish_services_with_comands(id)
    keys = configs.keys()
    return render_template(
        "finalizar.html",
        id=id,
        configs=configs,
        keys=keys,
        list_comands=list_comands,
        errors=errors,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )


@login_required
def config_import(id):
    transport_config = TransportConfig()
    config_imports = transport_config.get_configs_import(id)
    return render_template(
        "config_import.html",
        id=id,
        config_imports=config_imports,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
    )
