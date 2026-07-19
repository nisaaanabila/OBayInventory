from flask import Blueprint, render_template, session, redirect

staff = Blueprint("staff", __name__)


# =====================================================
# DASHBOARD STAFF
# =====================================================

@staff.route("/staff/dashboard")
def dashboard_staff():

    # Belum login
    if "user_id" not in session:
        return redirect("/")

    # Hanya STAFF
    if session.get("role") != "STAFF":
        return redirect("/")

    return render_template(
        "dashboard.html",
        nama=session.get("nama"),
        role=session.get("role")
    )