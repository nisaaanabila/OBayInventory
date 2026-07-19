const API = "http://127.0.0.1:5000/api/staff";

const staffTable = document.getElementById("staffTable");
const staffForm = document.getElementById("staffForm");

const modal = document.getElementById("staffModal");
const btnTambah = document.getElementById("btnTambah");
const closeModal = document.getElementById("closeModal");
const modalTitle = document.getElementById("modalTitle");

const search = document.getElementById("searchStaff");

let editMode = false;


// ===========================
// LOAD STAFF
// ===========================

async function loadStaff() {

    try {

        const res = await fetch(API, {
            credentials: "include"
        });

        const result = await res.json();

        if (result.status !== "success") {
            alert(result.message);
            return;
        }

        staffTable.innerHTML = "";

        result.data.forEach(item => {

            staffTable.innerHTML += `

                <tr>

                    <td>${item.id_staff_tampilan}</td>

                    <td>${item.nama_staff}</td>

                    <td>${item.username}</td>

                    <td>${item.email ?? "-"}</td>

                    <td>${item.nomor_telepon ?? "-"}</td>

                    <td>

                        <span class="status ${item.status === "AKTIF" ? "aktif" : "nonaktif"}">

                            ${item.status}

                        </span>

                    </td>

                    <td>

                        <div class="action">

                            <button
                                class="edit"
                                onclick="editStaff(${item.id})">

                                <i class="fa-solid fa-pen"></i>

                            </button>

                            <button
                                class="delete"
                                onclick="hapusStaff(${item.id})">

                                <i class="fa-solid fa-trash"></i>

                            </button>

                        </div>

                    </td>

                </tr>

            `;

        });

    }

    catch (err) {

        console.error(err);

    }

}

loadStaff();


// ===========================
// BUKA MODAL TAMBAH
// ===========================

btnTambah.onclick = () => {

    staffForm.reset();

    editMode = false;

    modalTitle.innerHTML = "Tambah Staff";

    document.getElementById("staffId").value = "";

    document.getElementById("password").required = true;

    modal.classList.add("active");

};


// ===========================
// TUTUP MODAL
// ===========================

closeModal.onclick = () => {

    modal.classList.remove("active");

};

window.onclick = (e) => {

    if (e.target == modal) {

        modal.classList.remove("active");

    }

};


// ===========================
// SIMPAN
// ===========================

staffForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const id = document.getElementById("staffId").value;

    const data = {

        nama_staff: document.getElementById("nama").value,

        username: document.getElementById("username").value,

        email: document.getElementById("email").value,

        nomor_telepon: document.getElementById("telepon").value,

        password: document.getElementById("password").value,

        status: document.getElementById("status").value

    };

    let url = API;
    let method = "POST";

    if (editMode) {

        url = `${API}/${id}`;

        method = "PUT";

        if (data.password === "") {

            delete data.password;

        }

    }

    try {

        const res = await fetch(url, {

            method: method,

            credentials: "include",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify(data)

        });

        const result = await res.json();

        alert(result.message);

        if (result.status === "success") {

            modal.classList.remove("active");

            loadStaff();

        }

    }

    catch (err) {

        console.error(err);

    }

});


// ===========================
// EDIT STAFF
// ===========================

async function editStaff(id) {

    try {

        const res = await fetch(`${API}/${id}`, {

            credentials: "include"

        });

        const result = await res.json();

        const item = result.data;

        document.getElementById("staffId").value = item.id;

        document.getElementById("nama").value = item.nama_staff;

        document.getElementById("username").value = item.username;

        document.getElementById("email").value = item.email ?? "";

        document.getElementById("telepon").value = item.nomor_telepon ?? "";

        document.getElementById("status").value = item.status;

        document.getElementById("password").value = "";

        document.getElementById("password").required = false;

        editMode = true;

        modalTitle.innerHTML = "Edit Staff";

        modal.classList.add("active");

    }

    catch (err) {

        console.error(err);

    }

}


// ===========================
// HAPUS STAFF
// ===========================

async function hapusStaff(id) {

    if (!confirm("Yakin ingin menghapus staff ini?")) return;

    try {

        const res = await fetch(`${API}/${id}`, {

            method: "DELETE",

            credentials: "include"

        });

        const result = await res.json();

        alert(result.message);

        loadStaff();

    }

    catch (err) {

        console.error(err);

    }

}


// ===========================
// SEARCH
// ===========================

search.addEventListener("keyup", () => {

    const keyword = search.value.toLowerCase();

    const rows = document.querySelectorAll("#staffTable tr");

    rows.forEach(row => {

        row.style.display = row.innerText
            .toLowerCase()
            .includes(keyword)

            ? ""

            : "none";

    });

});