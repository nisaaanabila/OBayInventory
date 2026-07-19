const API = "/api";

let dataBarang = [];
let dataBarangFilter = [];
let dataBahan = [];

let deleteId = null;


// ======================================
// DOM READY
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    loadBahan();
    loadBarang();

    document
        .getElementById("btnTambah")
        .addEventListener("click", bukaModalTambah);

    document
        .getElementById("formBarang")
        .addEventListener("submit", simpanBarang);

    document
        .getElementById("searchInput")
        .addEventListener("input", cariBarang);

    document
        .getElementById("closeModal")
        .addEventListener("click", tutupModal);

    document
        .getElementById("cancelDelete")
        .addEventListener("click", () => {

            document
                .getElementById("modalDelete")
                .classList.remove("show");

        });

    document
        .getElementById("btnDelete")
        .addEventListener("click", prosesDelete);

});


// ======================================
// LOAD BARANG MASUK
// ======================================

async function loadBarang() {

    try {

        const response = await fetch(`${API}/barang-masuk`, {
            credentials: "include"
        });

        const result = await response.json();

        if (result.status !== "success") {

            Swal.fire(
                "Error",
                result.message,
                "error"
            );

            return;

        }

        dataBarang = result.data;

        dataBarangFilter = [...dataBarang];

        renderTable();

    }

    catch (err) {

        console.error(err);

        Swal.fire(
            "Error",
            "Gagal mengambil data barang masuk.",
            "error"
        );

    }

}


// ======================================
// LOAD BAHAN
// ======================================

async function loadBahan() {

    try {

        const response = await fetch(`${API}/bahan`, {
            credentials: "include"
        });

        const result = await response.json();

        if (result.status !== "success")
            return;

        dataBahan = result.data;

        let html = `
            <option value="">
                Pilih Bahan
            </option>
        `;

        dataBahan.forEach(item => {

            html += `
                <option value="${item.id}">
                    ${item.nama_bahan}
                    (${item.satuan})
                </option>
            `;

        });

        document
            .getElementById("bahanSelect")
            .innerHTML = html;

    }

    catch (err) {

        console.error(err);

    }

}


// ======================================
// SEARCH
// ======================================

function cariBarang() {

    const keyword = document
        .getElementById("searchInput")
        .value
        .toLowerCase();

    dataBarangFilter = dataBarang.filter(item => {

        return (

            item.nama_bahan
                .toLowerCase()
                .includes(keyword)

            ||

            (item.sumber_vendor || "")
                .toLowerCase()
                .includes(keyword)

            ||

            (item.nama_user || "")
                .toLowerCase()
                .includes(keyword)

        );

    });

    renderTable();

}
// ======================================
// RENDER TABLE
// ======================================

function renderTable() {

    const tbody =
        document.getElementById("tbodyBarang");

    if (dataBarangFilter.length === 0) {

        tbody.innerHTML = `

            <tr>

                <td colspan="7"
                    style="text-align:center;padding:30px;">

                    Tidak ada data barang masuk.

                </td>

            </tr>

        `;

        return;

    }

    let html = "";

    dataBarangFilter.forEach(item => {

        html += `

        <tr>

            <td>

                ${formatTanggal(item.tanggal)}

            </td>

            <td>

                ${item.nama_bahan}

            </td>

            <td>

                ${item.qty}

            </td>

            <td>

                ${item.satuan}

            </td>

            <td>

                ${item.sumber_vendor || "-"}

            </td>

            <td>

                ${item.nama_user || "-"}

            </td>

            <td>

                <button
                    class="btn-danger"
                    onclick="hapusBarang(${item.id})">

                    <i class="fas fa-trash"></i>

                </button>

            </td>

        </tr>

        `;

    });

    tbody.innerHTML = html;

}


// ======================================
// MODAL TAMBAH
// ======================================

function bukaModalTambah() {

    document
        .getElementById("formBarang")
        .reset();

    document
        .getElementById("tanggal")
        .value = new Date()
        .toISOString()
        .split("T")[0];

    document
        .getElementById("modalBarang")
        .classList.add("show");

}


// ======================================
// TUTUP MODAL
// ======================================

function tutupModal() {

    document
        .getElementById("modalBarang")
        .classList.remove("show");

}


// ======================================
// SIMPAN BARANG MASUK
// ======================================

async function simpanBarang(e) {

    e.preventDefault();

    const data = {

        tanggal:
            document.getElementById("tanggal").value,

        bahan_id:
            document.getElementById("bahanSelect").value,

        qty:
            document.getElementById("qty").value,

        sumber_vendor:
            document.getElementById("sumber_vendor").value,

        keterangan:
            document.getElementById("keterangan").value

            };

            try {

                const response = await fetch(`${API}/barang-masuk`, {

            method: "POST",

            credentials: "include",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        });

        const result =
            await response.json();

        if (result.status !== "success") {

            Swal.fire(

                "Gagal",

                result.message,

                "error"

            );

            return;

        }

        Swal.fire({

            icon: "success",

            title: "Berhasil",

            text: result.message,

            timer: 1500,

            showConfirmButton: false

        });

        tutupModal();

        loadBarang();

    }

    catch (err) {

        console.error(err);

        Swal.fire(

            "Error",

            "Terjadi kesalahan.",

            "error"

        );

    }

}
// ======================================
// HAPUS BARANG
// ======================================

function hapusBarang(id) {

    deleteId = id;

    document
        .getElementById("modalDelete")
        .classList.add("show");

}


// ======================================
// PROSES DELETE
// ======================================

async function prosesDelete() {

    if (deleteId === null)
        return;

    try {

        const response = await fetch(`${API}/barang-masuk/${deleteId}`, {

    method: "DELETE",

    credentials: "include"

});

        const result = await response.json();

        if (result.status !== "success") {

            Swal.fire(

                "Gagal",

                result.message,

                "error"

            );

            return;

        }

        document
            .getElementById("modalDelete")
            .classList.remove("show");

        Swal.fire({

            icon: "success",

            title: "Berhasil",

            text: result.message,

            timer: 1500,

            showConfirmButton: false

        });

        deleteId = null;

        loadBarang();

    }

    catch (err) {

        console.error(err);

        Swal.fire(

            "Error",

            "Terjadi kesalahan.",

            "error"

        );

    }

}


// ======================================
// FORMAT TANGGAL
// ======================================

function formatTanggal(tanggal) {

    if (!tanggal) return "-";

    return tanggal.substring(0, 10).split("-").reverse().join("/");

}


// ======================================
// TUTUP MODAL SAAT KLIK DI LUAR
// ======================================

window.addEventListener("click", function (event) {

    const modalBarang =
        document.getElementById("modalBarang");

    const modalDelete =
        document.getElementById("modalDelete");

    if (event.target === modalBarang) {

        tutupModal();

    }

    if (event.target === modalDelete) {

        modalDelete.classList.remove("show");

    }

});


// ======================================
// ESC MENUTUP MODAL
// ======================================

document.addEventListener("keydown", function (e) {

    if (e.key === "Escape") {

        tutupModal();

        document
            .getElementById("modalDelete")
            .classList.remove("show");

    }

});


// ======================================
// REFRESH
// ======================================

function refreshData() {

    loadBarang();

}