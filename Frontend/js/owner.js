const API = "http://127.0.0.1:5000/api/owner";

const ownerTable = document.getElementById("ownerTable");
const ownerForm = document.getElementById("ownerForm");

const modal = document.getElementById("ownerModal");
const btnTambah = document.getElementById("btnTambah");
const closeModal = document.getElementById("closeModal");
const modalTitle = document.getElementById("modalTitle");

const search = document.getElementById("searchOwner");

let editMode = false;


// ===========================
// LOAD OWNER
// ===========================

async function loadOwner(){

    try{

        const res = await fetch(API,{
            credentials:"include"
        });

        const result = await res.json();

        ownerTable.innerHTML = "";

        result.data.forEach(item=>{

            ownerTable.innerHTML += `

                <tr>

                    <td>${item.id_owner_tampilan}</td>

                    <td>${item.nama_owner}</td>

                    <td>${item.username}</td>

                    <td>${item.email ?? "-"}</td>

                    <td>${item.nomor_telepon ?? "-"}</td>

                    <td>

                        <span class="status ${item.status=="AKTIF" ? "aktif":"nonaktif"}">

                            ${item.status}

                        </span>

                    </td>

                    <td>

                        <div class="action">

                            <button
                                class="edit"
                                onclick="editOwner(${item.id})">

                                <i class="fa-solid fa-pen"></i>

                            </button>

                            <button
                                class="delete"
                                onclick="hapusOwner(${item.id})">

                                <i class="fa-solid fa-trash"></i>

                            </button>

                        </div>

                    </td>

                </tr>

            `;

        });

    }

    catch(err){

        console.log(err);

    }

}

loadOwner();


// ===========================
// MODAL
// ===========================

btnTambah.onclick = ()=>{

    ownerForm.reset();

    editMode = false;

    modalTitle.innerHTML = "Tambah Owner";

    document.getElementById("ownerId").value = "";

    document.getElementById("password").required = true;

    modal.classList.add("active");

};


closeModal.onclick = ()=>{

    modal.classList.remove("active");

};


window.onclick = (e)=>{

    if(e.target==modal){

        modal.classList.remove("active");

    }

};


// ===========================
// SIMPAN
// ===========================

ownerForm.addEventListener("submit",async(e)=>{

    e.preventDefault();

    const id = document.getElementById("ownerId").value;

    const data={

        nama_owner:document.getElementById("nama").value,

        username:document.getElementById("username").value,

        email:document.getElementById("email").value,

        nomor_telepon:document.getElementById("telepon").value,

        password:document.getElementById("password").value,

        status:document.getElementById("status").value

    };

    let url = API;
    let method = "POST";

    if(editMode){

        url = `${API}/${id}`;
        method = "PUT";

        if(data.password===""){

            delete data.password;

        }

    }

    const res = await fetch(url,{

        method:method,

        credentials:"include",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify(data)

    });

    const result = await res.json();

    alert(result.message);

    if(result.status=="success"){

        modal.classList.remove("active");

        loadOwner();

    }

});


// ===========================
// EDIT
// ===========================

async function editOwner(id){

    const res = await fetch(`${API}/${id}`,{

        credentials:"include"

    });

    const result = await res.json();

    const item = result.data;

    document.getElementById("ownerId").value = item.id;

    document.getElementById("nama").value = item.nama_owner;

    document.getElementById("username").value = item.username;

    document.getElementById("email").value = item.email ?? "";

    document.getElementById("telepon").value = item.nomor_telepon ?? "";

    document.getElementById("status").value = item.status;

    document.getElementById("password").value = "";

    document.getElementById("password").required = false;

    editMode = true;

    modalTitle.innerHTML = "Edit Owner";

    modal.classList.add("active");

}


// ===========================
// DELETE
// ===========================

async function hapusOwner(id){

    if(!confirm("Yakin ingin menghapus owner ini?")) return;

    const res = await fetch(`${API}/${id}`,{

        method:"DELETE",

        credentials:"include"

    });

    const result = await res.json();

    alert(result.message);

    loadOwner();

}


// ===========================
// SEARCH
// ===========================

search.addEventListener("keyup",()=>{

    const keyword = search.value.toLowerCase();

    const rows = document.querySelectorAll("#ownerTable tr");

    rows.forEach(row=>{

        row.style.display = row.innerText.toLowerCase().includes(keyword)

        ? ""

        : "none";

    });

});