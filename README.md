# O'Bay Inventory

Aplikasi manajemen inventory berbasis web untuk mencatat dan mengelola stok bahan baku, produk, resep, vendor, hingga purchase order (PO). Dibuat sebagai proyek tugas kuliah/skripsi.

Fitur

- **Login** dengan Google OAuth (role-based: Owner & Staff)
- **Dashboard** ringkasan data inventory
- **Manajemen Bahan Baku** — tambah, lihat, ubah, hapus data bahan
- **Manajemen Produk** — data produk yang dijual/diproduksi
- **Manajemen Resep** — komposisi bahan untuk tiap produk
- **Manajemen Vendor** — data pemasok bahan baku
- **Barang Masuk** — pencatatan stok masuk dari vendor
- **Penggunaan Bahan** — pencatatan pemakaian bahan baku
- **Purchase Order (PO)** — pembuatan dan pengelolaan PO ke vendor
- **Upload gambar produk** via Cloudinary

Tech Stack

| Kategori | Teknologi |
|---|---|
| Backend | Flask (Python) |
| Database | TiDB Cloud (MySQL-compatible) |
| Autentikasi | Google OAuth 2.0 (Authlib) |
| Penyimpanan gambar | Cloudinary |
| Deployment | Vercel |

Struktur Folder

```
OBayInventory/
│
├── app.py                 # Entry point aplikasi Flask
├── config.py               # Konfigurasi environment (.env)
├── requirements.txt         # Daftar dependency Python
├── vercel.json              # Konfigurasi deployment Vercel
│
├── database/
│   └── connection.py        # Koneksi ke database TiDB
│
├── routes/
│   ├── login.py
│   ├── dashboard.py
│   ├── owner.py
│   ├── staff.py
│   ├── bahan.py
│   ├── barang_masuk.py
│   ├── produk.py
│   ├── penggunaan.py
│   ├── vendor.py
│   ├── resep.py
│   └── po.py
│
├── templates/                # File HTML (Jinja2)
│
└── static/
    ├── css/
    ├── js/
    └── images/
```

Desain (Figma)

[Lihat desain UI di Figma](https://www.figma.com/design/iWr0S0NhOtT2nmEGcrIAOs/O-Bay-Inventoryy)

Cara Menjalankan Secara Lokal

1. **Clone repository**
   ```bash
   git clone https://github.com/nisaaanabila/OBayInventory.git
   cd OBayInventory
   ```

2. **Buat virtual environment & install dependency**
   ```bash
   python -m venv venv
   venv\Scripts\activate       # Windows
   source venv/bin/activate    # macOS/Linux

   pip install -r requirements.txt
   ```

3. **Konfigurasi environment variable**

   Salin `.env.example` menjadi `.env`, lalu isi dengan kredensial masing-masing:
   ```bash
   cp .env.example .env
   ```

   Isi variabel berikut di `.env`:
   - `FLASK_SECRET_KEY`
   - `TIDB_HOST`, `TIDB_USER`, `TIDB_PASSWORD`, `TIDB_PORT`, `TIDB_DATABASE`
   - `CLOUDINARY_URL`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

4. **Jalankan aplikasi**
   ```bash
   python app.py
   ```

   Aplikasi akan berjalan di `http://localhost:5000`


