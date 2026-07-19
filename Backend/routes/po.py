from flask import (Blueprint,jsonify,request,session,send_file)
from Backend.database.connection import get_connection

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from reportlab.platypus import (SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer)

po = Blueprint("po", __name__)

def owner_only():

    if "user_id" not in session:

        return jsonify({

            "status": "error",
            "message": "Unauthorized"

        }),401


    if session.get("role") != "OWNER":

        return jsonify({

            "status":"error",
            "message":"Hanya Owner yang memiliki akses."

        }),403

    return None

# GENERATE KODE PO
def generate_kode_po(conn):

    today = datetime.now().strftime("%Y%m%d")

    with conn.cursor() as cursor:

        cursor.execute("""

            SELECT COUNT(*) total

            FROM purchase_orders

            WHERE DATE(created_at)=CURDATE()

        """)

        nomor = cursor.fetchone()["total"] + 1

    return f"PO-{today}-{nomor:03d}"

# GET PURCHASE ORDER
@po.route("/api/purchase-orders", methods=["GET"])
def get_purchase_orders():

    auth = owner_only()

    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT

                    p.id,
                    p.kode_po,
                    p.tanggal,
                    p.status,

                    v.nama_vendor

                FROM purchase_orders p

                JOIN vendors v

                    ON p.vendor_id=v.id

                ORDER BY p.created_at DESC

            """)

            data = cursor.fetchall()

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

# DETAIL PURCHASE ORDER
@po.route("/api/purchase-orders/<int:id>", methods=["GET"])
def detail_po(id):

    auth = owner_only()

    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT *

                FROM purchase_orders

                WHERE id=%s

            """,(id,))

            po_data = cursor.fetchone()

            if not po_data:

                return jsonify({

                    "status":"error",
                    "message":"Purchase Order tidak ditemukan."

                }),404


            cursor.execute("""

                SELECT

                    d.id,

                    b.nama_bahan,

                    d.qty,

                    d.harga,

                    d.subtotal

                FROM purchase_order_detail d

                JOIN bahan_baku b

                ON d.bahan_id=b.id

                WHERE d.po_id=%s

            """,(id,))

            detail = cursor.fetchall()


        return jsonify({

            "status":"success",

            "purchase_order":po_data,

            "detail":detail

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        }),500

    finally:

        conn.close()
# TAMBAH PURCHASE ORDER
@po.route("/api/purchase-orders", methods=["POST"])
def tambah_purchase_order():

    auth = owner_only()

    if auth:
        return auth

    data = request.get_json()

    vendor_id = data.get("vendor_id")
    tanggal = data.get("tanggal")
    estimasi = data.get("estimasi_pengiriman")
    catatan = data.get("catatan")
    detail = data.get("detail", [])

    if not vendor_id:

        return jsonify({

            "status": "error",
            "message": "Vendor harus dipilih."

        }), 400

    if len(detail) == 0:

        return jsonify({

            "status": "error",
            "message": "Minimal satu bahan harus dipilih."

        }), 400

    conn = get_connection()

    try:

        conn.begin()

        kode_po = generate_kode_po(conn)

        with conn.cursor() as cursor:

            cursor.execute("""

                INSERT INTO purchase_orders(

                    kode_po,
                    vendor_id,
                    tanggal,
                    estimasi_pengiriman,
                    catatan,
                    created_by

                )

                VALUES(%s,%s,%s,%s,%s,%s)

            """, (

                kode_po,
                vendor_id,
                tanggal,
                estimasi,
                catatan,
                session["user_id"]

            ))

            po_id = cursor.lastrowid
            total = 0
            for item in detail:

                qty = float(item["qty"])
                harga = float(item.get("harga", 0))
                subtotal = qty * harga
                total+=subtotal

                cursor.execute("""

                    INSERT INTO purchase_order_detail(

                        po_id,
                        bahan_id,
                        qty,
                        harga,
                        subtotal

                    )

                    VALUES(%s,%s,%s,%s,%s)

                """, (

                    po_id,
                    item["bahan_id"],
                    qty,
                    harga,
                    subtotal

                ))

        conn.commit()

        return jsonify({

            "status": "success",
            "message": "Purchase Order berhasil dibuat.",
            "po_id": po_id,
            "kode_po": kode_po

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()

# EDIT PURCHASE ORDER
@po.route("/api/purchase-orders/<int:id>", methods=["PUT"])
def edit_purchase_order(id):

    auth = owner_only()

    if auth:
        return auth

    data=request.get_json()

    conn=get_connection()

    try:

        conn.begin()

        with conn.cursor() as cursor:

            cursor.execute("""

                UPDATE purchase_orders

                SET

                    vendor_id=%s,
                    tanggal=%s,
                    estimasi_pengiriman=%s,
                    catatan=%s

                WHERE id=%s

            """,(

                data["vendor_id"],
                data["tanggal"],
                data.get("estimasi_pengiriman"),
                data.get("catatan"),
                id

            ))

            cursor.execute("""

                DELETE

                FROM purchase_order_detail

                WHERE po_id=%s

            """,(id,))

            total=0

            for item in data["detail"]:

                subtotal=float(item["qty"])*float(item["harga"])

                total+=subtotal

                cursor.execute("""

                    INSERT INTO purchase_order_detail(

                        po_id,
                        bahan_id,
                        qty,
                        harga,
                        subtotal

                    )

                    VALUES(%s,%s,%s,%s,%s)

                """,(

                    id,
                    item["bahan_id"],
                    item["qty"],
                    item["harga"],
                    subtotal

                ))

            cursor.execute("""

                UPDATE purchase_orders

                SET total=%s

                WHERE id=%s

            """,(total,id))

        conn.commit()

        return jsonify({

            "status":"success",
            "message":"Purchase Order berhasil diperbarui."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status":"error",
            "message":str(e)

        }),500

    finally:

        conn.close()

# DELETE PURCHASE ORDER
@po.route("/api/purchase-orders/<int:id>",methods=["DELETE"])
def delete_po(id):

    auth=owner_only()

    if auth:
        return auth

    conn=get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                DELETE

                FROM purchase_orders

                WHERE id=%s

            """,(id,))

        conn.commit()

        return jsonify({

            "status":"success",
            "message":"Purchase Order berhasil dihapus."

        })

    finally:

        conn.close()

# UPDATE STATUS PURCHASE ORDER
@po.route("/api/purchase-orders/<int:id>/status",methods=["PUT"])
def update_status_po(id):

    auth=owner_only()

    if auth:
        return auth

    data=request.get_json()

    conn=get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                UPDATE purchase_orders

                SET status=%s

                WHERE id=%s

            """,(

                data["status"],
                id

            ))

        conn.commit()

        return jsonify({

            "status":"success",
            "message":"Status berhasil diperbarui."

        })

    finally:

        conn.close()


# LIST VENDOR UNTUK PURCHASE ORDER
@po.route("/api/vendors-po", methods=["GET"])
def list_vendor_po():

    auth = owner_only()
    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    nama_vendor
                FROM vendors
                WHERE status='Active'
                ORDER BY nama_vendor
            """)

            data = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": data
        })

    except Exception as e:
        print("ERROR VENDOR PO:", e)   # <-- TAMBAHKAN INI

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        conn.close()

# BAHAN BERDASARKAN VENDOR
@po.route("/api/vendors-po/<int:id>/bahan", methods=["GET"])
def bahan_vendor(id):

    auth = owner_only()

    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT

                    id,
                    nama_bahan,
                    satuan,
                    stok_saat_ini

                FROM bahan_baku

                WHERE vendor_id=%s

                ORDER BY nama_bahan

            """,(id,))

            data=cursor.fetchall()

        return jsonify({

            "status":"success",

            "data":data

        })

    finally:

        conn.close()



# DOWNLOAD PDF PURCHASE ORDER
@po.route("/api/purchase-orders/<int:id>/pdf", methods=["GET"])
def download_pdf(id):

    auth = owner_only()

    if auth:
        return auth

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            # HEADER PO
            cursor.execute("""

                SELECT
                    p.*,
                    v.nama_vendor,
                    v.nomor_telepon,
                    v.email

                FROM purchase_orders p

                JOIN vendors v
                    ON p.vendor_id = v.id

                WHERE p.id=%s

            """, (id,))

            po_data = cursor.fetchone()

            if not po_data:

                return jsonify({

                    "status": "error",
                    "message": "Purchase Order tidak ditemukan."

                }), 404

            # DETAIL PO
            cursor.execute("""

                SELECT
                    b.nama_bahan,
                    d.qty,
                    d.harga,
                    d.subtotal

                FROM purchase_order_detail d

                JOIN bahan_baku b
                    ON d.bahan_id = b.id

                WHERE d.po_id=%s

            """, (id,))

            detail = cursor.fetchall()

        # MEMBUAT PDF
        buffer = BytesIO()

        doc = SimpleDocTemplate(

            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm

        )

        styles = getSampleStyleSheet()

        elements = []

        elements.append(
            Paragraph(
                "<b><font size='18'>O'Bay Coffee</font></b>",
                styles["Title"]
            )
        )

        elements.append(
            Paragraph(
                "PURCHASE ORDER",
                styles["Heading2"]
            )
        )

        elements.append(Spacer(1, 0.5 * cm))

        elements.append(
            Paragraph(
                f"<b>No PO :</b> {po_data['kode_po']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Tanggal :</b> {po_data['tanggal']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Vendor :</b> {po_data['nama_vendor']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>No WA :</b> {po_data['nomor_telepon']}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Email :</b> {po_data['email'] or '-'}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 0.7 * cm))

        # TABEL
        table_data = [

            ["No", "Bahan", "Qty", "Harga", "Subtotal"]

        ]

        total = 0

        for i, item in enumerate(detail, start=1):

            table_data.append([

                str(i),
                item["nama_bahan"],
                str(item["qty"]),
                f"Rp {item['harga']:,.0f}",
                f"Rp {item['subtotal']:,.0f}"

            ])

            total += item["subtotal"]

        table_data.append([

            "",
            "",
            "",
            "TOTAL",
            f"Rp {total:,.0f}"

        ])

        table = Table(

            table_data,

            colWidths=[

                1.2 * cm,
                7 * cm,
                2.5 * cm,
                3 * cm,
                3 * cm

            ]

        )

        table.setStyle(TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 1, colors.black),

            ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),

            ("BACKGROUND", (-2, -1), (-1, -1), colors.lightgrey),

            ("ALIGN", (0, 0), (-1, -1), "CENTER"),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 10)

        ]))

        elements.append(table)

        if po_data["catatan"]:

            elements.append(Spacer(1, 0.5 * cm))

            elements.append(

                Paragraph(

                    f"<b>Catatan :</b><br/>{po_data['catatan']}",

                    styles["Normal"]

                )

            )

        doc.build(elements)

        buffer.seek(0)

        return send_file(

            buffer,

            as_attachment=True,

            download_name=f"{po_data['kode_po']}.pdf",

            mimetype="application/pdf"

        )

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500

    finally:

        conn.close()