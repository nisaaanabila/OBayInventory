from flask import Blueprint, jsonify, session, render_template, redirect, url_for
from Backend.database.connection import get_connection

dashboard = Blueprint("dashboard", __name__)

# HALAMAN DASHBOARD
@dashboard.route("/dashboard")
def dashboard_page():

    print("SESSION =", dict(session))

    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        nama=session.get("nama"),
        role=session.get("role")
    )


# DASHBOARD API
@dashboard.route("/api/dashboard", methods=["GET"])
def dashboard_data():

    if "user_id" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # SUMMARY CARD
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM bahan_baku
            """)
            total_bahan = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM produk
            """)
            total_produk = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM vendors
                WHERE status='Active'
            """)
            total_vendor = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM bahan_baku
                WHERE stok_saat_ini <= minimum_stok
            """)
            stok_menipis = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM barang_masuk
                WHERE DATE(tanggal)=CURDATE()
            """)
            barang_masuk_hari_ini = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM penggunaan_bahan
                WHERE DATE(tanggal)=CURDATE()
            """)
            penggunaan_hari_ini = cursor.fetchone()["total"]

            # CRITICAL INVENTORY
            cursor.execute("""
                SELECT
                    nama_bahan,
                    stok_saat_ini,
                    minimum_stok,
                    satuan,
                    CASE
                        WHEN stok_saat_ini = 0 THEN 'KRITIS'
                        WHEN stok_saat_ini <= minimum_stok THEN 'MENIPIS'
                        ELSE 'AMAN'
                    END AS status
                FROM bahan_baku
                WHERE stok_saat_ini <= minimum_stok
                ORDER BY stok_saat_ini ASC
            """)

            critical_inventory = cursor.fetchall()


            # BARANG MASUK TERBARU
            cursor.execute("""
                SELECT
                    bm.tanggal,
                    b.nama_bahan,
                    bm.qty,
                    b.satuan,
                    u.nama_user
                FROM barang_masuk bm
                JOIN bahan_baku b
                    ON bm.bahan_id = b.id
                LEFT JOIN users u
                    ON bm.user_id = u.id
                ORDER BY bm.id DESC
                LIMIT 5
            """)

            barang_masuk = cursor.fetchall()

            # PENGGUNAAN TERBARU
            cursor.execute("""
                SELECT
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
                LIMIT 5
            """)

            penggunaan = cursor.fetchall()

        return jsonify({

            "status": "success",

            "summary": {

                "total_bahan": total_bahan,
                "total_produk": total_produk,
                "total_vendor": total_vendor,
                "stok_menipis": stok_menipis,
                "barang_masuk_hari_ini": barang_masuk_hari_ini,
                "penggunaan_hari_ini": penggunaan_hari_ini

            },

            "critical_inventory": critical_inventory,
            "barang_masuk_terbaru": barang_masuk,
            "penggunaan_terbaru": penggunaan

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()

