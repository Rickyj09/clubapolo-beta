from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si ya está logueado, no mostrar login otra vez
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Buscar por username o email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        # ❌ Credenciales incorrectas
        if not user or not user.check_password(password):
            flash("Usuario o contraseña incorrectos", "danger")
            return render_template("login.html")

        # ❌ Usuario inactivo
        if not user.is_active:
            flash("Usuario inactivo. Contacte al administrador.", "warning")
            return render_template("login.html")

        # ✅ Login correcto
        login_user(user)
        flash(f"Bienvenido {user.username}", "success")

        # 🔐 Forzar cambio de contraseña
        if user.must_change_password:
            return redirect(url_for("profile.index"))

        # 🎯 Redirección por rol
        if user.has_role("ADMIN"):
            return redirect(url_for("admin.dashboard"))

        if user.has_role("PROFESOR"):
            return redirect(url_for("alumnos.index"))

        # Fallback
        return redirect(url_for("public.home"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("public.home"))
