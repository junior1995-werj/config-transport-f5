import os

from flask import Flask, request, redirect, render_template
from flask_login import LoginManager, current_user, login_required
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

from config import settings
from handler.user.user import User
from handler.gtm.routes import wide_ip, server_ip, datacenter, server_gtm, pool_wide_ip
from handler.ltm.routes import (
    nat,
    pool,
    snat,
    irule,
    monitor,
    policies,
    profiles,
    datagroup,
    snat_pool,
    virtual_server,
)
from handler.user.routes import login, logout, register
from handler.big_ip.big_ip import BigIpProcess, TransportConfig
from handler.big_ip.routes import bigip, finalizar, config_import
from handler.system.routes import (
    icall,
    users,
    chassis,
    folders,
    sys_device,
    user_alert,
    devicegroup,
    system_module,
    traffic_group,
    system_information,
)
from handler.network.routes import (
    vlans,
    trunks,
    self_ip,
    interfaces,
    routes_domains,
    routes_statics,
    packet_filters_rule,
)
from handler.utils.socket_events import (
    connect,
    connecting,
    server_event,
    event_add_config,
    event_remove_config,
    event_update_config,
    event_delete_connection,
    event_add_config_default,
    send_services_new_big_ip,
    event_add_config_by_filter,
    event_remove_config_finish,
    event_add_all_config_default,
)
from handler.ltm.generic_message.routes import (
    peer,
    route,
    router,
    protocol,
    transport_config,
)

login_manager = LoginManager()

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")
list_external_id_send_configurations = []
login_manager.init_app(app)

# ---------------------------------------------------- Routes ----------------------------------------------------


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user.load_user_get_by_id(int(user_id))


@app.errorhandler(401)
def not_found(e):
    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error=error, status_code_error=404)


@app.errorhandler(500)
def error_system(error):
    return render_template("error.html", error=error, status_code_error=500)


@app.route("/index")
@login_required
def index():
    query = BigIpProcess()
    upload = request.args.get("upload")
    filename = request.args.get("filename")
    if not upload:
        upload = False
        filename = ""
    else:
        upload = True
    connections = query.get_connections()
    return render_template(
        "index.html",
        connections=connections,
        url_socket=settings.SERVER_SOCKET,
        username=current_user.username,
        upload=upload,
        filename=filename,
    )


@app.route("/new_config")
@login_required
def new_config():
    return render_template(
        "new_config.html",
        username=current_user.username,
        url_socket=settings.SERVER_SOCKET,
    )


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if request.method == "POST":
        f = request.files["file"]
        filename = secure_filename(f.filename)

        if not os.path.exists(settings.UPLOAD_FOLDER):
            os.mkdir(settings.UPLOAD_FOLDER)
        f.save(os.path.join(settings.UPLOAD_FOLDER, filename))

    return redirect(f"/index?upload=true&filename={filename}")


@app.route("/bigip/alter_config/<uuid:id>", methods=["POST"])
@login_required
def alter_config(id):
    if request.method == "POST":
        transport_config = TransportConfig()
        transport_config.update(request.form)
        print(request)
    return redirect(f"/bigip/finalizar/{id}")


@app.route("/bigip/send_config/<uuid:id>", methods=["POST"])
@login_required
def send_config(id):
    if request.method == "POST":
        username = request.values["username"]
        host = request.values["host"]
        password = request.values["password"]
        return render_template(
            "send_config.html",
            id=id,
            username=username,
            host=host,
            password=password,
            url_socket=settings.SERVER_SOCKET,
        )


# --------------------------------------------- Routes - User ----------------------------------------------------
app.add_url_rule("/register", methods=["GET", "POST"], view_func=register)
app.add_url_rule("/", methods=["GET", "POST"], view_func=login)
app.add_url_rule("/logout", view_func=logout)

# -------------------------------------------- Routes - big-ip ---------------------------------------------------

app.add_url_rule("/bigip/<uuid:id>", view_func=bigip)
app.add_url_rule("/bigip/finalizar/<uuid:id>", view_func=finalizar)
app.add_url_rule("/bigip/config_import/<uuid:id>", view_func=config_import)

# ---------------------------------------------- Routes - LTM ----------------------------------------------------

app.add_url_rule("/bigip/pool/<uuid:id>", view_func=pool)
app.add_url_rule("/bigip/virtual_server/<uuid:id>", view_func=virtual_server)
app.add_url_rule("/bigip/datagroup/<uuid:id>", view_func=datagroup)
app.add_url_rule("/bigip/irule/<uuid:id>", view_func=irule)
app.add_url_rule("/bigip/monitor/<uuid:id>", view_func=monitor)
app.add_url_rule("/bigip/profiles/<uuid:id>", view_func=profiles)
app.add_url_rule("/bigip/policies/<uuid:id>", view_func=policies)
app.add_url_rule("/bigip/snat/<uuid:id>", view_func=snat)
app.add_url_rule("/bigip/snat_pool/<uuid:id>", view_func=snat_pool)
app.add_url_rule("/bigip/nat/<uuid:id>", view_func=nat)

# -------------------------------------------- Routes - Network ----------------------------------------------------

app.add_url_rule("/bigip/vlans/<uuid:id>", view_func=vlans)
app.add_url_rule("/bigip/trunks/<uuid:id>", view_func=trunks)
app.add_url_rule("/bigip/self_ip/<uuid:id>", view_func=self_ip)
app.add_url_rule("/bigip/routes_statics/<uuid:id>", view_func=routes_statics)
app.add_url_rule("/bigip/interfaces/<uuid:id>", view_func=interfaces)
app.add_url_rule("/bigip/routes_domains/<uuid:id>", view_func=routes_domains)
app.add_url_rule("/bigip/packet_filters_rule/<uuid:id>", view_func=packet_filters_rule)

# -------------------------------------------- Routes - System ----------------------------------------------------

app.add_url_rule("/bigip/system_information/<uuid:id>", view_func=system_information)
app.add_url_rule("/bigip/devicegroup/<uuid:id>", view_func=devicegroup)
app.add_url_rule("/bigip/folders/<uuid:id>", view_func=folders)
app.add_url_rule("/bigip/system_module/<uuid:id>", view_func=system_module)
app.add_url_rule("/bigip/sys_device/<uuid:id>", view_func=sys_device)
app.add_url_rule("/bigip/icall/<uuid:id>", view_func=icall)
app.add_url_rule("/bigip/traffic_group/<uuid:id>", view_func=traffic_group)
app.add_url_rule("/bigip/chassis/<uuid:id>", view_func=chassis)
app.add_url_rule("/bigip/users/<uuid:id>", view_func=users)
app.add_url_rule("/bigip/user_alert/<uuid:id>", view_func=user_alert)


# ---------------------------------------------- Routes - GTM -----------------------------------------------------

app.add_url_rule("/bigip/datacenter/<uuid:id>", view_func=datacenter)
app.add_url_rule("/bigip/server_gtm/<uuid:id>", view_func=server_gtm)
app.add_url_rule("/bigip/server_ip/<uuid:id>", view_func=server_ip)
app.add_url_rule("/bigip/wide_ip/<uuid:id>", view_func=wide_ip)
app.add_url_rule("/bigip/pool_wide_ip/<uuid:id>", view_func=pool_wide_ip)


# ---------------------------------------------- Routes - GM -----------------------------------------------------

app.add_url_rule("/bigip/peer/<uuid:id>", view_func=peer)
app.add_url_rule("/bigip/route/<uuid:id>", view_func=route)
app.add_url_rule("/bigip/router/<uuid:id>", view_func=router)
app.add_url_rule("/bigip/transport_config/<uuid:id>", view_func=transport_config)
app.add_url_rule("/bigip/protocol/<uuid:id>", view_func=protocol)

# ---------------------------------------------------- Events ----------------------------------------------------

socketio.on_event("event_delete_connection", event_delete_connection)
socketio.on_event("event_add_all_config_default", event_add_all_config_default)
socketio.on_event("event_add_config_default", event_add_config_default)
socketio.on_event("event_remove_config", event_remove_config)
socketio.on_event("event_remove_config_finish", event_remove_config_finish)
socketio.on_event("event_update_config", event_update_config)
socketio.on_event("connect", connect)
socketio.on_event("connecting", connecting)
socketio.on_event("event_add_config", event_add_config)
socketio.on_event("send_services_new_big_ip", send_services_new_big_ip)
socketio.on_event("event_add_config_by_filter", event_add_config_by_filter)
socketio.on_event("server_event", server_event)

# ---------------------------------------------------- Init ----------------------------------------------------

if __name__ == "__main__":
    socketio.run(app=app, host="0.0.0.0", debug=True, allow_unsafe_werkzeug=True)
