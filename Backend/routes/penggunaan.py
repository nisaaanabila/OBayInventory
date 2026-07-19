from flask import Blueprint, jsonify, request, session
from decimal import Decimal
from Backend.database.connection import get_connection

penggunaan = Blueprint("penggunaan", __name__)


# ======================================================
# GET DATA PENGGUNAAN
# ======================================================

@penggunaan.route("/api/penggunaan", methods=["GET"])
def get_penggunaan():

    if "user_id" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT

                    pb.id,
                    pb.tanggal,
                    p.nama_produk,
                    pb.qty_terjual,
                    u.nama_user

                FROM penggunaan_bahan pb

                JOIN produk p
                    ON pb.produk_id = p.id

                JOIN users u
                    ON pb.user_id = u.id

                ORDER BY pb.id DESC

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


# ======================================================
# TAMBAH PENGGUNAAN
# ======================================================

@penggunaan.route("/api/penggunaan", methods=["POST"])
def tambah_penggunaan():

    if "user_id" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    data = request.json

    produk_id = data["produk_id"]

    qty_terjual = int(data["qty_terjual"])

    if qty_terjual <= 0:

        return jsonify({

            "status": "error",
            "message": "Qty terjual harus lebih dari 0"

        }), 400

    user_id = session["user_id"]

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # ===========================
            # Cek Produk
            # ===========================

            cursor.execute("""

                SELECT id

                FROM produk

                WHERE id=%s

            """, (produk_id,))

            if cursor.fetchone() is None:

                return jsonify({

                    "status": "error",
                    "message": "Produk tidak ditemukan"

                }), 404

            # ===========================
            # Simpan Header Penggunaan
            # ===========================

            cursor.execute("""

                INSERT INTO penggunaan_bahan
                (
                    tanggal,
                    produk_id,
                    qty_terjual,
                    user_id
                )

                VALUES
                (
                    NOW(),
                    %s,
                    %s,
                    %s
                )

            """, (

                produk_id,
                qty_terjual,
                user_id

            ))

            penggunaan_id = cursor.lastrowid

            # ===========================
            # Ambil Resep Produk
            # ===========================

            cursor.execute("""

                SELECT

                    r.bahan_id,
                    r.takaran,
                    b.nama_bahan,
                    b.stok_saat_ini

                FROM resep r

                JOIN bahan_baku b

                    ON r.bahan_id = b.id

                WHERE r.produk_id=%s

            """, (produk_id,))

            resep = cursor.fetchall()

            if len(resep) == 0:

                conn.rollback()

                return jsonify({

                    "status": "error",
                    "message": "Produk belum memiliki resep."

                }), 400

            # ===========================
            # Validasi Stok
            # ===========================

            for item in resep:

                kebutuhan = Decimal(str(item["takaran"])) * qty_terjual

                stok = Decimal(str(item["stok_saat_ini"]))

                if kebutuhan > stok:

                    conn.rollback()

                    return jsonify({

                        "status": "error",
                        "message": f"Stok {item['nama_bahan']} tidak mencukupi."

                    }), 400

            # ===========================
            # Update Stok
            # ===========================

            for item in resep:

                bahan_id = item["bahan_id"]

                qty_awal = Decimal(str(item["stok_saat_ini"]))

                qty_digunakan = Decimal(str(item["takaran"])) * qty_terjual

                qty_sisa = qty_awal - qty_digunakan

                if qty_sisa < 0:
                    qty_sisa = Decimal("0")

                cursor.execute("""

                    UPDATE bahan_baku

                    SET stok_saat_ini=GREATEST(%s, 0)

                    WHERE id=%s

                """, (

                    float(qty_sisa),
                    bahan_id

                ))

                cursor.execute("""

                    INSERT INTO detail_penggunaan
                    (
                        penggunaan_id,
                        bahan_id,
                        qty_awal,
                        qty_digunakan,
                        qty_sisa
                    )

                    VALUES
                    (%s,%s,%s,%s,%s)

                """, (

                    penggunaan_id,
                    bahan_id,
                    float(qty_awal),
                    float(qty_digunakan),
                    float(qty_sisa)

                ))

        conn.commit()

        return jsonify({

            "status": "success",
            "message": "Penggunaan bahan berhasil dicatat."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()


# ======================================================
# DETAIL PENGGUNAAN
# ======================================================

@penggunaan.route("/api/penggunaan/<int:id>", methods=["GET"])
def detail_penggunaan(id):

    if "user_id" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT

                    b.nama_bahan,
                    dp.qty_awal,
                    dp.qty_digunakan,
                    dp.qty_sisa

                FROM detail_penggunaan dp

                JOIN bahan_baku b

                    ON dp.bahan_id = b.id

                WHERE dp.penggunaan_id=%s

            """, (id,))

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