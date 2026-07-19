from flask import (Blueprint,jsonify,request,session,render_template,redirect,url_for)
from Backend.database.connection import get_connection

barang_masuk = Blueprint("barang_masuk", __name__)

# ==========================================================
# HELPER AUTHORIZATION
# ==========================================================

def check_login():

    if "user_id" not in session:
        return False

    if session["role"] not in ["OWNER", "STAFF"]:
        return False

    return True

# ==========================================================
# HALAMAN BARANG MASUK
# ==========================================================

@barang_masuk.route("/barang-masuk")
def halaman_barang_masuk():

    if not check_login():
        return redirect(url_for("home"))

    return render_template(
        "barang_masuk.html",
        nama=session.get("nama"),
        role=session.get("role")
    )


# ==========================================================
# GET BARANG MASUK
# ==========================================================

@barang_masuk.route("/api/barang-masuk", methods=["GET"])
def get_barang_masuk():

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

            bm.id,

            bm.tanggal,

            bm.bahan_id,

            b.nama_bahan,

            bm.qty,

            b.satuan,

            COALESCE(bm.sumber_vendor,'') AS sumber_vendor,

            COALESCE(bm.keterangan,'') AS keterangan,

            COALESCE(u.nama_user,'-') AS nama_user

        FROM barang_masuk bm

        JOIN bahan_baku b
            ON bm.bahan_id = b.id

        LEFT JOIN users u
            ON bm.user_id = u.id

        ORDER BY bm.tanggal DESC,
                bm.id DESC

        """)

        data = cursor.fetchall()
        print(data)
        print(type(data[0]["tanggal"]))
        print(data[0]["tanggal"])

        # Ubah objek date menjadi string
        for item in data:
            if item["tanggal"]:
                item["tanggal"] = item["tanggal"].strftime("%Y-%m-%d")

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


# ==========================================================
# TAMBAH BARANG MASUK
# ==========================================================

@barang_masuk.route("/api/barang-masuk", methods=["POST"])
def tambah_barang_masuk():

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

                SELECT

                    id

                FROM bahan_baku

                WHERE id=%s

            """,(data["bahan_id"],))

            bahan = cursor.fetchone()

            if not bahan:

                return jsonify({

                    "status":"error",

                    "message":"Bahan tidak ditemukan"

                }),404

            cursor.execute("""

                INSERT INTO barang_masuk
                (

                    tanggal,

                    bahan_id,

                    qty,

                    sumber_vendor,

                    keterangan,

                    user_id

                )

                VALUES
                (%s,%s,%s,%s,%s,%s)

            """,(

                data["tanggal"],

                data["bahan_id"],

                data["qty"],

                data["sumber_vendor"],

                data.get("keterangan",""),

                session["user_id"]

            ))

            cursor.execute("""

                UPDATE bahan_baku

                SET stok_saat_ini=stok_saat_ini+%s

                WHERE id=%s

            """,(

                data["qty"],

                data["bahan_id"]

            ))

            conn.commit()

        return jsonify({

            "status":"success",

            "message":"Barang masuk berhasil ditambahkan"

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",

            "message":str(e)

        }),500
    finally:

        conn.close()


# ==========================================================
# DELETE BARANG MASUK
# ==========================================================

@barang_masuk.route("/api/barang-masuk/<int:id>", methods=["DELETE"])
def delete_barang_masuk(id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # Ambil data barang masuk

            cursor.execute("""

                SELECT

                    bahan_id,

                    qty

                FROM barang_masuk

                WHERE id=%s

            """, (id,))

            barang = cursor.fetchone()

            if not barang:

                return jsonify({

                    "status": "error",

                    "message": "Data tidak ditemukan"

                }), 404

            # Kurangi stok bahan, tapi jangan sampai minus.
            # GREATEST(stok_saat_ini - qty, 0) memastikan hasilnya
            # minimal 0, bukan angka negatif.

            cursor.execute("""

                UPDATE bahan_baku

                SET stok_saat_ini = GREATEST(stok_saat_ini - %s, 0)

                WHERE id = %s

            """, (

                barang["qty"],

                barang["bahan_id"]

            ))

            # Hapus transaksi

            cursor.execute("""

                DELETE FROM barang_masuk

                WHERE id = %s

            """, (id,))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Barang masuk berhasil dihapus"

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()