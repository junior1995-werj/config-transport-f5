from flask import render_template
from flask_login import current_user, login_required

from handler.big_ip.big_ip import TransportConfig
from handler.system.system import System


@login_required
def system_information(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    system_informations = query.get_static_system_information_by_id(id)
    return render_template(
        "system/system_information.html",
        system_informations=system_informations,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def devicegroup(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    devicegroups = query.get_static_devicegroup_by_id(id)
    return render_template(
        "system/devicegroup.html",
        devicegroups=devicegroups,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def folders(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    folders = query.get_static_folder_by_id(id)
    return render_template(
        "system/folders.html",
        folders=folders,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def system_module(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    system_modules = query.get_static_system_module_by_id(id)
    return render_template(
        "system/system_modules.html",
        system_modules=system_modules,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def sys_device(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    sys_devices = query.get_static_sys_device_by_id(id)
    return render_template(
        "system/sys_devices.html",
        sys_devices=sys_devices,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def chassis(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    chassis = query.get_static_chassis_by_id(id)
    return render_template(
        "system/chassis.html",
        chassis=chassis,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def icall(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    icalls = query.get_static_icall_by_id(id)
    return render_template(
        "system/icall.html",
        icalls=icalls,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def traffic_group(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    traffic_groups = query.get_static_traffic_group_by_id(id)
    return render_template(
        "system/traffic_group.html",
        traffic_groups=traffic_groups,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def users(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    users = query.get_static_users_by_id(id)
    return render_template(
        "system/users.html",
        users=users,
        id=id,
        configs=configs,
        username=current_user.username,
    )


@login_required
def user_alert(id):
    transport_config = TransportConfig()
    configs = transport_config.get_transport_config(id)
    query = System()
    users = query.get_user_alert_by_id(id)
    return render_template(
        "system/user_alert.html",
        users=users,
        id=id,
        configs=configs,
        username=current_user.username,
    )
