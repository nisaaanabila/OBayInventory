from flask import Blueprint, render_template, session, redirect

owner = Blueprint("owner", __name__)


# ============================================
# DASHBOARD OWNER
# ============================================

@owner.route("/owner/dashboard")
def dashboard_owner():

    # Belum login
    if "user_id" not in session:
        return redirect("/")

    # Bukan owner
    if session.get("role") != "OWNER":
        return redirect("/")

    return render_template(
        "dashboard.html",
        nama=session.get("nama"),
        role=session.get("role")
    )

@owner.route("/penggunaan")
def penggunaan_page():

    if "user_id" not in session:
        return redirect("/")

    return render_template(
        "penggunaan.html",
        nama=session.get("nama"),
        role=session.get("role")
    )