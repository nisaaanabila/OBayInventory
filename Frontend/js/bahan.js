const API = "/api";

let dataBahan = [];
let dataVendor = [];
let deleteId = null;

const tbody = document.getElementById("tbodyBahan");

const searchInput = document.getElementById("searchInput");

const modalForm = document.getElementById("modalForm");

const modalDelete = document.getElementById("modalDelete");

const form = document.getElementById("formBahan");

const modalTitle = document.getElementById("modalTitle");

const btnTambah = document.getElementById("btnTambah");

const closeModal = document.getElementById("closeModal");

const btnDelete = document.getElementById("btnDelete");

const cancelDelete = document.getElementById("cancelDelete");

document.addEventListener("DOMContentLoaded", () => {

    loadVendor();

    loadBahan();

    btnTambah.addEventListener("click", tambahBaru);

    closeModal.addEventListener("click", () => {

        modalForm.classList.remove("show");

    });

    cancelDelete.addEventListener("click", () => {

        modalDelete.classList.remove("show");

    });

    form.addEventListener("submit", simpanBahan);

    btnDelete.addEventListener("click", deleteBahan);

    searchInput.addEventListener("keyup", cariBahan);

});

async function loadBahan() {

    try {

        const response = await fetch(`${API}/bahan`);

        const result = await response.json();

        if (result.status !== "success") {

            alert(result.message);

            return;

        }

        dataBahan = result.data;

        renderTable(dataBahan);

    }

    catch (err) {

        console.error(err);

        alert("Gagal mengambil data bahan.");

    }

}

async function loadVendor() {

    try {

        const response = await fetch(`${API}/vendors`);

        const result = await response.json();

        if (result.status !== "success") return;

        dataVendor = result.data;

        let html = `
            <option value="">
                Tanpa Vendor
            </option>
        `;

        dataVendor.forEach(v => {

            html += `
                <option value="${v.id}">
                    ${v.nama_vendor}
                </option>
            `;

        });

        document.getElementById("vendor_id").innerHTML = html;

    }

    catch (err) {

        console.error(err);

    }

}

function renderTable(data) {

    tbody.innerHTML = "";

    if (data.length === 0) {

        tbody.innerHTML = `

            <tr>

                <td colspan="8" style="text-align:center;padding:30px;">

                    Tidak ada data.

                </td>

            </tr>

        `;

        return;

    }

    data.forEach(item => {

        let badge = "";

        if (item.status_stok === "KRITIS") {

            badge = `<span class="badge badge-danger">KRITIS</span>`;

        }

        else if (item.status_stok === "MENIPIS") {

            badge = `<span class="badge badge-warning">MENIPIS</span>`;

        }

        else {

            badge = `<span class="badge badge-success">AMAN</span>`;

        }

        tbody.innerHTML += `

            <tr>

                <td>${item.sku}</td>

                <td>${item.nama_bahan}</td>

                <td>${item.satuan}</td>

                <td>${item.stok_saat_ini}</td>

                <td>${item.minimum_stok}</td>

                <td>${item.nama_vendor ?? "-"}</td>

                <td>${badge}</td>

                <td>

                    <div class="action">

                        <button
                            class="edit-btn"
                            onclick="editBahan(${item.id})">

                            <i class="fas fa-pen"></i>

                        </button>

                        <button
                            class="delete-btn"
                            onclick="confirmDelete(${item.id})">

                            <i class="fas fa-trash"></i>

                        </button>

                    </div>

                </td>

            </tr>

        `;

    });

}

function cariBahan() {

    const keyword = searchInput.value.toLowerCase();

    const hasil = dataBahan.filter(item =>

        item.nama_bahan.toLowerCase().includes(keyword) ||

        item.sku.toLowerCase().includes(keyword)

    );

    renderTable(hasil);

}

function tambahBaru() {

    form.reset();

    document.getElementById("id").value = "";

    document.getElementById("vendor_id").value = "";

    modalTitle.textContent = "Tambah Bahan";

    modalForm.classList.add("show");

}

function editBahan(id) {

    const item = dataBahan.find(b => b.id == id);

    if (!item) return;

    modalTitle.textContent = "Edit Bahan";

    document.getElementById("id").value = item.id;

    document.getElementById("sku").value = item.sku;

    document.getElementById("nama_bahan").value = item.nama_bahan;

    document.getElementById("satuan").value = item.satuan;

    document.getElementById("stok_saat_ini").value = item.stok_saat_ini;

    document.getElementById("minimum_stok").value = item.minimum_stok;

    document.getElementById("vendor_id").value = item.vendor_id ?? "";

    modalForm.classList.add("show");

}

async function simpanBahan(e) {

    e.preventDefault();

    const id = document.getElementById("id").value;

    const data = {

        sku: document.getElementById("sku").value,

        nama_bahan: document.getElementById("nama_bahan").value,

        satuan: document.getElementById("satuan").value,

        stok_saat_ini: parseFloat(
            document.getElementById("stok_saat_ini").value
        ),

        minimum_stok: parseFloat(
            document.getElementById("minimum_stok").value
        ),

        vendor_id:
            document.getElementById("vendor_id").value || null

    };

    let url = `${API}/bahan`;

    let method = "POST";

    if (id !== "") {

        url = `${API}/bahan/${id}`;

        method = "PUT";

    }

    try {

        const response = await fetch(url, {

            method,

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const result = await response.json();

        alert(result.message);

        if (result.status === "success") {

            modalForm.classList.remove("show");

            form.reset();

            loadBahan();

        }

    }

    catch (err) {

        console.error(err);

        alert("Terjadi kesalahan saat menyimpan data.");

    }

}

function confirmDelete(id) {

    deleteId = id;

    modalDelete.classList.add("show");

}

async function deleteBahan() {

    if (!deleteId) return;

    try {

        const response = await fetch(`${API}/bahan/${deleteId}`, {

            method: "DELETE"

        });

        const result = await response.json();

        alert(result.message);

        if (result.status === "success") {

            modalDelete.classList.remove("show");

            deleteId = null;

            loadBahan();

        }

    }

    catch (err) {

        console.error(err);

        alert("Gagal menghapus data.");

    }

}

window.addEventListener("click", (e) => {

    if (e.target === modalForm) {

        modalForm.classList.remove("show");

    }

    if (e.target === modalDelete) {

        modalDelete.classList.remove("show");

    }

});

document.addEventListener("keydown", (e) => {

    if (e.key === "Escape") {

        modalForm.classList.remove("show");

        modalDelete.classList.remove("show");

    }

});

function resetForm() {

    form.reset();

    document.getElementById("id").value = "";

    document.getElementById("vendor_id").value = "";

}

closeModal.addEventListener("click", () => {

    modalForm.classList.remove("show");

    resetForm();

});

cancelDelete.addEventListener("click", () => {

    modalDelete.classList.remove("show");

    deleteId = null;

});

function refreshData() {

    loadVendor();

    loadBahan();

}