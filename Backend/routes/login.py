from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    url_for,
    redirect,
    current_app
)

from Backend.database.connection import get_connection

auth = Blueprint(
    "auth",
    __name__
)


# =====================================================
# LOGIN MANUAL
# =====================================================

@auth.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Data login tidak valid."
        }), 400


    login_input = data.get("email", "").strip()
    password = data.get("password", "").strip()


    if login_input == "" or password == "":
        return jsonify({
            "status": "error",
            "message": "Email / Username dan Password wajib diisi."
        }), 400


    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # ===============================
            # LOGIN BISA EMAIL ATAU NAMA_USER
            # ===============================

            cursor.execute("""

                SELECT *

                FROM users

                WHERE
                    email=%s
                    OR nama_user=%s

                LIMIT 1

            """, (

                login_input,
                login_input

            ))

            user = cursor.fetchone()


            if not user:

                return jsonify({

                    "status": "error",
                    "message": "Email / Username tidak ditemukan."

                }),404


            # ===============================
            # PASSWORD
            # ===============================

            if password != user["password"]:

                return jsonify({

                    "status":"error",
                    "message":"Password salah."

                }),401


            # ===============================
            # SESSION
            # ===============================

            session.permanent = True

            session["user_id"] = user["id"]
            session["nama"] = user["nama_user"]
            session["role"] = user["role"]


            # ===============================
            # LOGIN LOG
            # ===============================

            cursor.execute("""

                INSERT INTO login_log
                (
                    user_id,
                    ip_address
                )

                VALUES(%s,%s)

            """,(

                user["id"],
                request.remote_addr

            ))

            conn.commit()


            return jsonify({

                "status":"success",

                "message":"Login berhasil.",

                "role":user["role"],

                "nama":user["nama_user"]

            })


    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",

            "message":str(e)

        }),500


    finally:

        conn.close()


# =====================================================
# GOOGLE LOGIN
# =====================================================

@auth.route("/api/google/login")
def google_login():

    google = current_app.extensions["google_oauth"]

    redirect_uri = url_for(
        "auth.google_authorize",
        _external=True
    )

    return google.authorize_redirect(redirect_uri)



# =====================================================
# GOOGLE CALLBACK
# =====================================================

@auth.route("/api/google/authorize")
def google_authorize():

    try:

        google = current_app.extensions["google_oauth"]

        google.authorize_access_token()

        resp = google.get("userinfo")

        user_info = resp.json()

        email = user_info.get("email")


        conn = get_connection()

        try:

            with conn.cursor() as cursor:

                cursor.execute("""

                    SELECT *

                    FROM users

                    WHERE email=%s

                    LIMIT 1

                """,(email,))

                user = cursor.fetchone()


                if not user:

                    return f"""

                    <h2>

                    Email <b>{email}</b>

                    belum terdaftar pada sistem.

                    </h2>

                    """,403


                session.permanent = True

                session["user_id"] = user["id"]
                session["nama"] = user["nama_user"]
                session["role"] = user["role"]


                cursor.execute("""

                    INSERT INTO login_log
                    (
                        user_id,
                        ip_address
                    )

                    VALUES(%s,%s)

                """,(

                    user["id"],
                    request.remote_addr

                ))

                conn.commit()


        finally:

            conn.close()



        # ==========================
        # REDIRECT KE DASHBOARD
        # ==========================

            return redirect("/dashboard")

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 400



# =====================================================
# SESSION
# =====================================================

@auth.route("/api/session")
def check_session():

    if "user_id" not in session:

        return jsonify({

            "status":"error",

            "message":"Belum login."

        }),401


    return jsonify({

        "status":"success",

        "user":{

            "id":session["user_id"],
            "nama":session["nama"],
            "role":session["role"]

        }

    })



# =====================================================
# LOGOUT
# =====================================================

@auth.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("home"))