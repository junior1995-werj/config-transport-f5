from flask import flash, request, redirect, render_template
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash

from config import settings
from handler.user.user import User


def login():
    if current_user.is_active:
        return redirect("/index")

    if request.method == "POST":
        user = User()

        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False
        user_model = user.get_user(username=username)

        if not user_model:
            flash("Usuario não encontrado.")
            return redirect("/")
        elif not check_password_hash(user_model.password, password):
            flash("Senha incorreta.")
            return redirect("/")

        login_user(user_model, remember=remember)

        return redirect("/index")

    return render_template("login.html", url_socket=settings.SERVER_SOCKET)


def register():
    if request.method == "POST":
        user = User()

        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")

        user_model = user.get_user(username=username)

        if not user_model:
            if " " in username:
                flash("username invalido! não permitido espaços")
                return render_template("register.html")
            user.create_user(name=name, username=username, password=password)
            return redirect("/")
        else:
            flash("Usuario ja existente!")

    return render_template("register.html")


@login_required
def logout():
    logout_user()
    return redirect("/")
