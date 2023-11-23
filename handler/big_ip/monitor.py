from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "seu_segredo_aqui"
socketio = SocketIO(app)


class Monitor:
    @staticmethod
    def create_connection_and_lists(process, model):
        if process:
            message = model
        else:
            message = model
        emit("server_origin", {"message": message, "process": process}, broadcast=True)

    @staticmethod
    def new_add_config_header(service, internal_id, external_id, id, model, all=False):

        line = '<tr id="tr_connections" class="tr_connections" >'
        line += f"<td>{ service } : </td>"
        line += f'<td>{ model["name"] } </td>'
        line += f"<td hidden>{ external_id }</td>"
        line += f"<td hidden>{ internal_id }</td>"
        line += f"<td hidden>{ id }</td>"
        line += '<td><button type="submit" data-toggle="tooltip" name="del" value="del" class="tr_clone_remove" data-placement="top" title="remover"><i class="mdi mdi-close"></i></button></td></tr>'
        emit("transport_config_new_line", {"message": line}, broadcast=True)

        if not all:
            emit("return_add", {"status": True}, broadcast=True)

    @staticmethod
    def get_all_config_add_header(models):
        line = ""
        for model in models:
            line = '<a class="link border-top" id="lines_header">'
            line += '<table class="table" id="zero_config"><thead><tr>'
            line += f'<th scope="col">{model["service"]}</th>'
            line += '<th scope="col">Remover</th></tr></thead><tbody>'
            line += '<tr id="tr_connections" class="tr_connections">'
            line += f'<td >Nome: {model["name"]} </td>'
            line += f'<td hidden>{model["external_id"]}</td><td hidden>{model["internal_id"]}</td><td hidden>{model["id"]}</td>'
            line += '<td><button type="submit" data-toggle="tooltip" name="add" value="add" class="tr_clone_add"'
            line += 'data-placement="top" title="Adicionar"><i class="mdi mdi-close"></i></button></td></tr></tbody></table></a>'

        emit("transport_config_all", {"message": line}, broadcast=True)

    @staticmethod
    def send_return_alert(message, status=False):
        emit("return_add", {"message": message, "status": status}, broadcast=True)

    @staticmethod
    def get_collor_text(status):
        dict_collor = {
            200: 'class="text-success"',
            400: 'class="text-danger"',
            401: 'class="text-danger"',
            404: 'class="text-danger"',
            409: 'class="text-warning"',
        }
        return dict_collor[status]

    def send_status_process_import(self, status, service, name_service, reason):
        line = '<tr id="tr_connections" class="tr_connections" >'
        line += f"<td {self.get_collor_text(status)}>{ status}</td>"
        line += f"<td>{ service } </td>"
        line += f"<td>{ name_service }</td>"
        line += f"<td>{ reason } </td></tr>"
        emit("process_execute", {"message": line}, broadcast=True)

    @staticmethod
    def send_status_progres_bar(message, status):
        emit(
            "event_process_file_status",
            {"message": message, "status": status},
            broadcast=True,
        )
