from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from Backend.database.connection import get_connection

resep = Blueprint(
    "resep",
    __name__
)

def check_login():

    if "user_id" not in session:
        return False

    return session.get("role") in ["OWNER", "STAFF"]

@resep.route("/api/resep/<int:produk_id>", methods=["GET"])
def get_resep(produk_id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM produk

                WHERE id=%s

            """, (produk_id,))

            produk = cursor.fetchone()

            if not produk:

                return jsonify({

                    "status": "error",

                    "message": "Produk tidak ditemukan."

                }), 404

            cursor.execute("""

                SELECT

                    r.id,

                    r.produk_id,

                    r.bahan_id,

                    b.nama_bahan,

                    r.takaran,

                    b.satuan,

                    b.stok_saat_ini,

                    b.minimum_stok,

                    CASE

                        WHEN b.stok_saat_ini = 0
                            THEN 'KRITIS'

                        WHEN b.stok_saat_ini <= b.minimum_stok
                            THEN 'MENIPIS'

                        ELSE 'AMAN'

                    END status_stok

                FROM resep r

                JOIN bahan_baku b
                    ON r.bahan_id = b.id

                WHERE r.produk_id = %s

                ORDER BY b.nama_bahan ASC

            """, (produk_id,))

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

@resep.route("/api/resep", methods=["POST"])
def tambah_resep():

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

            """, (data["produk_id"],))

            if not cursor.fetchone():

                return jsonify({

                    "status": "error",

                    "message": "Produk tidak ditemukan."

                }), 404

            cursor.execute("""

                SELECT id

                FROM bahan_baku

                WHERE id=%s

            """, (data["bahan_id"],))

            if not cursor.fetchone():

                return jsonify({

                    "status": "error",

                    "message": "Bahan tidak ditemukan."

                }), 404

            cursor.execute("""

                SELECT id

                FROM resep

                WHERE produk_id=%s
                AND bahan_id=%s

            """, (

                data["produk_id"],
                data["bahan_id"]

            ))

            if cursor.fetchone():

                return jsonify({

                    "status": "error",

                    "message": "Bahan sudah ada pada resep."

                }), 400

            cursor.execute("""

                INSERT INTO resep
                (

                    produk_id,

                    bahan_id,

                    takaran

                )

                VALUES
                (

                    %s,

                    %s,

                    %s

                )

            """, (

                data["produk_id"],

                data["bahan_id"],

                data["takaran"]

            ))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Resep berhasil ditambahkan."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()

@resep.route("/api/resep/<int:id>", methods=["PUT"])
def update_resep(id):

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

                FROM resep

                WHERE id=%s

            """, (id,))

            if not cursor.fetchone():

                return jsonify({

                    "status": "error",

                    "message": "Data resep tidak ditemukan."

                }), 404


            cursor.execute("""

                UPDATE resep

                SET

                    bahan_id=%s,

                    takaran=%s

                WHERE id=%s

            """, (

                data["bahan_id"],

                data["takaran"],

                id

            ))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Resep berhasil diperbarui."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()

@resep.route("/api/resep/<int:id>", methods=["DELETE"])
def delete_resep(id):

    if not check_login():

        return jsonify({

            "status": "error",

            "message": "Unauthorized"

        }), 401

    if session.get("role") != "OWNER":

        return jsonify({

            "status": "error",

            "message": "Hanya OWNER yang dapat menghapus resep."

        }), 403

    conn = get_connection()

    try:

        with conn.cursor() as cursor:

            cursor.execute("""

                SELECT id

                FROM resep

                WHERE id=%s

            """, (id,))

            if not cursor.fetchone():

                return jsonify({

                    "status": "error",

                    "message": "Data resep tidak ditemukan."

                }), 404


            cursor.execute("""

                DELETE

                FROM resep

                WHERE id=%s

            """, (id,))

            conn.commit()

        return jsonify({

            "status": "success",

            "message": "Resep berhasil dihapus."

        })

    except Exception as e:

        conn.rollback()

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

    finally:

        conn.close()