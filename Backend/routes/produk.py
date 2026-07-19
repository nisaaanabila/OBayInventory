from flask import (
    Blueprint,
    jsonify,
    request,
    session,
    render_template,
    redirect,
    url_for
)

from Backend.database.connection import get_connection

produk = Blueprint("produk", __name__)

def check_login():

    if "user_id" not in session:
        return False

    return session.get("role") in ["OWNER", "STAFF"]


@produk.route("/produk")
def halaman_produk():

    if not check_login():
        return redirect(url_for("home"))

    return render_template(
        "produk.html",
        nama=session.get("nama"),
        role=session.get("role")
    )


@produk.route("/api/produk", methods=["GET"])
def get_produk():

    if not check_login():

        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT

                    id,
                    kode_produk,
                    nama_produk,
                    kategori,
                    harga,
                    gambar_url,
                    status

                FROM produk

                ORDER BY nama_produk ASC

            """)

            data = cursor.fetchall()

        return jsonify({

            "status": "success",
            "data": data

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()

@produk.route("/api/produk/<int:id>", methods=["GET"])
def detail_produk(id):

    if not check_login():

        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT *

                FROM produk

                WHERE id=%s

            """, (id,))

            data = cursor.fetchone()

            if not data:

                return jsonify({

                    "status": "error",
                    "message": "Produk tidak ditemukan"

                }), 404

        return jsonify({

            "status": "success",
            "data": data

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()

@produk.route("/api/produk", methods=["POST"])
def tambah_produk():

    if not check_login():

        return jsonify({
            "status":"error",
            "message":"Unauthorized"
        }),401

    data = request.get_json()

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM produk

                WHERE kode_produk=%s

            """, (

                data["kode_produk"],

            ))

            cek = cursor.fetchone()

            if cek:

                return jsonify({

                    "status": "error",

                    "message": "Kode produk sudah digunakan."

                }), 400

            cursor.execute("""

                INSERT INTO produk
                (

                    kode_produk,
                    nama_produk,
                    kategori,
                    harga,
                    gambar_url,
                    status

                )

                VALUES
                (%s,%s,%s,%s,%s,%s)

            """,(

                data["kode_produk"],
                data["nama_produk"],
                data["kategori"],
                data["harga"],
                data.get("gambar_url"),
                data.get("status","Aktif")

            ))

            conn.commit()

        return jsonify({

            "status":"success",
            "message":"Produk berhasil ditambahkan"

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()

@produk.route("/api/produk/<int:id>", methods=["PUT"])
def update_produk(id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    data = request.get_json()

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM produk

                WHERE id=%s

            """, (id,))

            cek = cursor.fetchone()

            if not cek:

                return jsonify({

                    "status": "error",

                    "message": "Produk tidak ditemukan."

                }), 404

            cursor.execute("""

                SELECT id

                FROM produk

                WHERE kode_produk=%s
                AND id<>%s

            """, (

                data["kode_produk"],
                id

            ))

            cek_kode = cursor.fetchone()

            if cek_kode:

                return jsonify({

                    "status": "error",

                    "message": "Kode produk sudah digunakan."

                }), 400

            cursor.execute("""

                UPDATE produk

                SET

                    kode_produk=%s,
                    nama_produk=%s,
                    kategori=%s,
                    harga=%s,
                    gambar_url=%s,
                    status=%s

                WHERE id=%s

            """, (

                data["kode_produk"],
                data["nama_produk"],
                data["kategori"],
                data["harga"],
                data.get("gambar_url"),
                data["status"],
                id

            ))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Produk berhasil diperbarui"

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()

@produk.route("/api/produk/<int:id>", methods=["DELETE"])
def delete_produk(id):

    if not check_login():

        return jsonify({
            "status":"error",
            "message":"Unauthorized"
        }),401

    if session.get("role") != "OWNER":

        return jsonify({

            "status":"error",
            "message":"Hanya OWNER yang dapat menghapus produk."

        }),403

    conn=get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM produk
                WHERE id=%s
            """, (id,))
            produk_data = cursor.fetchone()
            if not produk_data:
                return jsonify({
                    "status": "error",
                    "message": "Produk tidak ditemukan."
                }), 404
            
            cursor.execute("""
                SELECT COUNT(*) total
                FROM resep
                WHERE produk_id=%s
            """, (id,))
            resep = cursor.fetchone()["total"]
            if resep > 0:
                return jsonify({
                    "status": "error",
                    "message": "Produk masih digunakan pada resep."
                }), 400

            cursor.execute("""

                DELETE

                FROM produk

                WHERE id=%s

            """, (id,))

            if cursor.rowcount == 0:

                conn.rollback()

                return jsonify({

                    "status":"error",

                    "message":"Produk gagal dihapus."

                }),400

            conn.commit()


        return jsonify({

            "status":"success",
            "message":"Produk berhasil dihapus"

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()