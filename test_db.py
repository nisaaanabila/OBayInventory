from Backend.database.connection import get_connection

try:

    conn = get_connection()

    print("✅ Berhasil konek TiDB")

    conn.close()

except Exception as e:

    print(e)