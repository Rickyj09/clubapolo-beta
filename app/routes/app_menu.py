from flask_login import login_required
from flask import Blueprint, abort, render_template


app_menu_bp = Blueprint(
    "app_menu",
    __name__,
    url_prefix="/menu"
)

@app_menu_bp.route("/")
@login_required
def menu():
    return render_template("app/menu.html")
