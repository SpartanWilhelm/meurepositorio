from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from auth.models import User
from database import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.get(request.form["username"])
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("stocks.dashboard"))
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not User.query.get(request.form["username"]):
            user = User(id=request.form["username"])
            user.set_password(request.form["password"])
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/reset/<username>")
@login_required
def reset_password(username):
    if not current_user.is_admin:
        return "Acesso negado", 403

    user = User.query.get(username)
    user.set_password("123")
    db.session.commit()
    return f"Senha do usuário {username} resetada para 123"

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
