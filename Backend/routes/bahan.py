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

bahan = Blueprint(
    "bahan",
    __name__
)


# ==========================================================
# AUTHORIZATION
# ==========================================================

def check_login():

    if "user_id" not in session:
        return False

    if session.get("role") not in ["OWNER", "STAFF"]:
        return False

    return True


# ==========================================================
# HALAMAN BAHAN BAKU
# ==========================================================

@bahan.route("/bahan")
def halaman_bahan():

    if not check_login():
        return redirect(url_for("home"))

    return render_template(
        "bahan.html",
        nama=session["nama"],
        role=session["role"]
    )


# ==========================================================
# GET SEMUA BAHAN
# ==========================================================

@bahan.route("/api/bahan", methods=["GET"])
def get_bahan():

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

                    b.id,
                    b.sku,
                    b.nama_bahan,
                    b.satuan,
                    b.stok_saat_ini,
                    b.minimum_stok,
                    b.vendor_id,

                    v.nama_vendor,

                    CASE

                        WHEN b.stok_saat_ini = 0
                            THEN 'KRITIS'

                        WHEN b.stok_saat_ini <= b.minimum_stok
                            THEN 'MENIPIS'

                        ELSE 'AMAN'

                    END status_stok

                FROM bahan_baku b

                LEFT JOIN vendors v
                ON b.vendor_id = v.id

                ORDER BY b.nama_bahan ASC

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


# ==========================================================
# GET DETAIL BAHAN
# ==========================================================

@bahan.route("/api/bahan/<int:id>", methods=["GET"])
def detail_bahan(id):

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

                FROM bahan_baku

                WHERE id=%s

            """, (id,))

            data = cursor.fetchone()

            if not data:

                return jsonify({

                    "status": "error",

                    "message": "Data tidak ditemukan."

                }), 404

        return jsonify({

            "status": "success",

            "data": data

        })

    finally:

        conn.close()


# ==========================================================
# TAMBAH BAHAN
# ==========================================================

@bahan.route("/api/bahan", methods=["POST"])
def tambah_bahan():

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    data = request.get_json()

    nama_bahan = (data.get("nama_bahan") or "").strip()
    stok_saat_ini = data.get("stok_saat_ini", 0) or 0
    minimum_stok = data.get("minimum_stok", 0) or 0

    if not nama_bahan:

        return jsonify({

            "status": "error",

            "message": "Nama bahan tidak boleh kosong."

        }), 400

    if float(stok_saat_ini) < 0 or float(minimum_stok) < 0:

        return jsonify({

            "status": "error",

            "message": "Stok dan minimum stok tidak boleh bernilai negatif."

        }), 400

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE sku=%s

            """, (

                data.get("sku"),

            ))

            cek = cursor.fetchone()

            if cek:

                return jsonify({

                    "status": "error",

                    "message": "SKU sudah digunakan."

                }), 400


            # ===========================
            # CEK NAMA BAHAN SUDAH ADA
            # (case-insensitive, abaikan spasi)
            # ===========================

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE LOWER(TRIM(nama_bahan)) = LOWER(TRIM(%s))

            """, (

                nama_bahan,

            ))

            cek_nama = cursor.fetchone()

            if cek_nama:

                return jsonify({

                    "status": "error",

                    "message": "Nama bahan sudah digunakan. Gunakan nama yang berbeda atau tambahkan stok pada bahan yang sudah ada."

                }), 400


            cursor.execute("""

                INSERT INTO bahan_baku
                (
                    sku,
                    nama_bahan,
                    satuan,
                    stok_saat_ini,
                    minimum_stok,
                    vendor_id
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )

            """, (

                data.get("sku"),
                nama_bahan,
                data.get("satuan"),
                stok_saat_ini,
                minimum_stok,
                data.get("vendor_id") or None

            ))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Bahan berhasil ditambahkan."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()


# ==========================================================
# UPDATE BAHAN
# ==========================================================

@bahan.route("/api/bahan/<int:id>", methods=["PUT"])
def update_bahan(id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    data = request.get_json()

    nama_bahan = (data.get("nama_bahan") or "").strip()
    stok_saat_ini = data.get("stok_saat_ini", 0) or 0
    minimum_stok = data.get("minimum_stok", 0) or 0

    if not nama_bahan:

        return jsonify({

            "status": "error",

            "message": "Nama bahan tidak boleh kosong."

        }), 400

    if float(stok_saat_ini) < 0 or float(minimum_stok) < 0:

        return jsonify({

            "status": "error",

            "message": "Stok dan minimum stok tidak boleh bernilai negatif."

        }), 400

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE id=%s

            """, (id,))

            cek = cursor.fetchone()

            if not cek:

                return jsonify({

                    "status": "error",

                    "message": "Data tidak ditemukan."

                }), 404


            # ===========================
            # CEK SKU DIPAKAI BAHAN LAIN
            # ===========================

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE sku=%s AND id != %s

            """, (

                data.get("sku"),
                id

            ))

            cek_sku = cursor.fetchone()

            if cek_sku:

                return jsonify({

                    "status": "error",

                    "message": "SKU sudah digunakan bahan lain."

                }), 400


            # ===========================
            # CEK NAMA BAHAN DIPAKAI BAHAN LAIN
            # (case-insensitive, abaikan spasi)
            # ===========================

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE LOWER(TRIM(nama_bahan)) = LOWER(TRIM(%s)) AND id != %s

            """, (

                nama_bahan,
                id

            ))

            cek_nama = cursor.fetchone()

            if cek_nama:

                return jsonify({

                    "status": "error",

                    "message": "Nama bahan sudah digunakan bahan lain. Gunakan nama yang berbeda."

                }), 400


            cursor.execute("""

                UPDATE bahan_baku

                SET

                    sku=%s,
                    nama_bahan=%s,
                    satuan=%s,
                    stok_saat_ini=%s,
                    minimum_stok=%s,
                    vendor_id=%s

                WHERE id=%s

            """, (

                data.get("sku"),
                nama_bahan,
                data.get("satuan"),
                stok_saat_ini,
                minimum_stok,
                data.get("vendor_id") or None,
                id

            ))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Data berhasil diperbarui."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()

# ==========================================================
# HAPUS BAHAN
# HANYA OWNER
# ==========================================================

@bahan.route("/api/bahan/<int:id>", methods=["DELETE"])
def delete_bahan(id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401


    if session.get("role") != "OWNER":

        return jsonify({

            "status": "error",

            "message": "Hanya OWNER yang dapat menghapus data."

        }), 403


    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # ===========================
            # CEK DATA
            # ===========================

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE id=%s

            """, (id,))

            bahan = cursor.fetchone()

            if not bahan:

                return jsonify({

                    "status": "error",

                    "message": "Data tidak ditemukan."

                }), 404


            # ===========================
            # CEK DIPAKAI BARANG MASUK
            # ===========================

            cursor.execute("""

                SELECT COUNT(*) total

                FROM barang_masuk

                WHERE bahan_id=%s

            """, (id,))

            barang_masuk = cursor.fetchone()["total"]


            # ===========================
            # CEK DIPAKAI RESEP
            # ===========================

            cursor.execute("""

                SELECT COUNT(*) total

                FROM resep

                WHERE bahan_id=%s

            """, (id,))

            resep = cursor.fetchone()["total"]


            # ===========================
            # CEK DIPAKAI PENGGUNAAN
            # ===========================

            cursor.execute("""

                SELECT COUNT(*) total

                FROM penggunaan_bahan_detail

                WHERE bahan_id=%s

            """, (id,))

            penggunaan = cursor.fetchone()["total"]


            if barang_masuk > 0 or resep > 0 or penggunaan > 0:

                return jsonify({

                    "status": "error",

                    "message":
                    "Data tidak dapat dihapus karena masih digunakan pada transaksi."

                }), 400


            # ===========================
            # DELETE
            # ===========================

            cursor.execute("""

                DELETE

                FROM bahan_baku

                WHERE id=%s

            """, (id,))

            conn.commit()


        return jsonify({

            "status": "success",

            "message": "Data berhasil dihapus."

        })


    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


    finally:

        conn.close()