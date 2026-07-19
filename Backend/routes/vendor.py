from flask import Blueprint, jsonify, request, session, render_template, redirect
from Backend.database.connection import get_connection

from flask import send_file
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

vendor = Blueprint("vendor", __name__)

@vendor.route("/vendor")
def halaman_vendor():

    if "user_id" not in session:
        return redirect("/")

    return render_template(
        "vendor.html",
        role=session.get("role")
    )

def owner_only():

    if "user_id" not in session:
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    if session.get("role") != "OWNER":
        return jsonify({
            "status": "error",
            "message": "Hanya Owner yang memiliki akses."
        }), 403

    return None


@vendor.route("/api/vendors", methods=["GET"])
def get_vendor():

    auth = owner_only()
    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT
                    id,
                    id_vendor_tampilan,
                    nama_vendor,
                    barang_disuplai,
                    nomor_telepon,
                    email,
                    status,
                    created_at

                FROM vendors

                ORDER BY nama_vendor ASC

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
        }),500

    finally:

        conn.close()

@vendor.route("/api/vendors/<int:id>", methods=["GET"])
def detail_vendor(id):

    auth = owner_only()
    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT *

                FROM vendors

                WHERE id=%s

            """,(id,))

            data = cursor.fetchone()

            if not data:

                return jsonify({
                    "status":"error",
                    "message":"Vendor tidak ditemukan."
                }),404

        return jsonify({
            "status":"success",
            "data":data
        })

    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        }),500

    finally:

        conn.close()

@vendor.route("/api/vendors", methods=["POST"])
def tambah_vendor():

    auth = owner_only()
    if auth:
        return auth

    data = request.get_json()

    required = [

        "id_vendor_tampilan",
        "nama_vendor",
        "barang_disuplai",
        "nomor_telepon",
        "status"

    ]

    for field in required:

        if not data.get(field):

            return jsonify({

                "status":"error",
                "message":f"{field} wajib diisi."

            }),400

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM vendors

                WHERE id_vendor_tampilan=%s

            """,(data["id_vendor_tampilan"],))

            if cursor.fetchone():

                return jsonify({

                    "status":"error",
                    "message":"ID Vendor sudah digunakan."

                }),400


            cursor.execute("""

                SELECT id

                FROM vendors

                WHERE nama_vendor=%s

            """,(data["nama_vendor"],))

            if cursor.fetchone():

                return jsonify({

                    "status":"error",
                    "message":"Nama vendor sudah ada."

                }),400


            cursor.execute("""

                INSERT INTO vendors(

                    id_vendor_tampilan,
                    nama_vendor,
                    barang_disuplai,
                    nomor_telepon,
                    email,
                    status

                )

                VALUES(%s,%s,%s,%s,%s,%s)

            """,(

                data["id_vendor_tampilan"],
                data["nama_vendor"],
                data["barang_disuplai"],
                data["nomor_telepon"],
                data.get("email"),
                data["status"]

            ))

            conn.commit()

        return jsonify({

            "status":"success",
            "message":"Vendor berhasil ditambahkan."

        }),201

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()

@vendor.route("/api/vendors/<int:id>", methods=["PUT"])
def update_vendor(id):

    auth = owner_only()
    if auth:
        return auth

    data = request.get_json()

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM vendors

                WHERE id=%s

            """,(id,))

            if not cursor.fetchone():

                return jsonify({

                    "status":"error",
                    "message":"Vendor tidak ditemukan."

                }),404


            cursor.execute("""

                UPDATE vendors

                SET

                    nama_vendor=%s,
                    barang_disuplai=%s,
                    nomor_telepon=%s,
                    email=%s,
                    status=%s

                WHERE id=%s

            """,(

                data["nama_vendor"],
                data["barang_disuplai"],
                data["nomor_telepon"],
                data.get("email"),
                data["status"],
                id

            ))

            conn.commit()

        return jsonify({

            "status":"success",
            "message":"Vendor berhasil diperbarui."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()


@vendor.route("/api/vendors/<int:id>", methods=["DELETE"])
def delete_vendor(id):

    auth = owner_only()
    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM vendors

                WHERE id=%s

            """,(id,))

            if not cursor.fetchone():

                return jsonify({

                    "status":"error",
                    "message":"Vendor tidak ditemukan."

                }),404


            cursor.execute("""

                SELECT COUNT(*) total

                FROM bahan_baku

                WHERE vendor_id=%s

            """,(id,))

            total = cursor.fetchone()["total"]

            if total > 0:

                return jsonify({

                    "status":"error",
                    "message":"Vendor masih digunakan oleh bahan baku."

                }),400


            cursor.execute("""

                DELETE FROM vendors

                WHERE id=%s

            """,(id,))

            conn.commit()

        return jsonify({

            "status":"success",
            "message":"Vendor berhasil dihapus."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()

@vendor.route("/vendor/pdf")
def export_pdf_vendor():

    auth = owner_only()
    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT
                    id_vendor_tampilan,
                    nama_vendor,
                    barang_disuplai,
                    nomor_telepon,
                    email,
                    status

                FROM vendors

                ORDER BY nama_vendor ASC

            """)

            vendors = cursor.fetchall()

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4)
        )

        styles = getSampleStyleSheet()

        elements = []

        elements.append(
            Paragraph("<b>O'Bay Inventory</b>", styles["Title"])
        )

        elements.append(
            Paragraph("Laporan Data Vendor", styles["Heading2"])
        )

        table_data = [[
            "ID Vendor",
            "Nama Vendor",
            "Barang Disuplai",
            "WhatsApp",
            "Email",
            "Status"
        ]]

        for v in vendors:

            table_data.append([
                v["id_vendor_tampilan"],
                v["nama_vendor"],
                v["barang_disuplai"],
                v["nomor_telepon"],
                v["email"] or "-",
                v["status"]
            ])

        table = Table(table_data)

        table.setStyle(TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#5C3B1E")),

            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

            ("BACKGROUND", (0,1), (-1,-1), colors.beige),

            ("ALIGN", (0,0), (-1,-1), "CENTER"),

            ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ]))

        elements.append(table)

        doc.build(elements)

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="Laporan_Vendor.pdf",
            mimetype="application/pdf"
        )

    finally:

        conn.close()