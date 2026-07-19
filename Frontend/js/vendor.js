const API = "/api";

let dataVendor = [];
function formatNomor(nomor){

    nomor = nomor
        .replace(/\s/g,"")
        .replace(/-/g,"")
        .replace(/\+/g,"");

    if(nomor.startsWith("0")){

        nomor = "62" + nomor.substring(1);

    }

    return nomor;

}
let dataFilter = [];

document.addEventListener("DOMContentLoaded", () => {

    loadVendor();

    document
        .getElementById("searchVendor")
        .addEventListener("input", cariVendor);

    document
        .getElementById("btnTambahVendor")
        .addEventListener("click", bukaModalTambah);

    document
        .getElementById("formVendor")
        .addEventListener("submit", simpanVendor);

});

async function loadVendor(){

    try{

        const res = await fetch(`${API}/vendors`,{

            credentials:"include"

        });

        const result = await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Error",
                result.message,
                "error"
            );

            return;

        }

        dataVendor = result.data;
        dataFilter = [...dataVendor];

        renderVendor();

    }

    catch(err){

        console.log(err);

    }

}

function cariVendor(){

    const keyword = document
        .getElementById("searchVendor")
        .value
        .toLowerCase();

    dataFilter = dataVendor.filter(item=>{

        return (

            item.nama_vendor
                .toLowerCase()
                .includes(keyword)

            ||

            item.id_vendor_tampilan
                .toLowerCase()
                .includes(keyword)

        );

    });

    renderVendor();

}

function renderVendor(){

    const container =
    document.getElementById("vendorList");

    if(dataFilter.length==0){

        container.innerHTML=`

            <div class="empty">

                Belum ada vendor.

            </div>

        `;

        return;

    }

    let html="";

    dataFilter.forEach(item=>{

        html+=`

        <div class="vendor-card">

            <div class="vendor-header">

                <h3>

                    ${item.nama_vendor}

                </h3>

                <span class="badge ${item.status.toLowerCase()}">

                    ${item.status}

                </span>

            </div>

            <div class="vendor-info">

                <p>

                    <i class="fas fa-id-card"></i>

                    ${item.id_vendor_tampilan}

                </p>

                <p>

                    <i class="fas fa-box"></i>

                    ${item.barang_disuplai}

                </p>

                <p>

                    <i class="fas fa-phone"></i>

                    ${item.nomor_telepon}

                </p>

                <p>

                    <i class="fas fa-envelope"></i>

                    ${item.email ?? "-"}

                </p>

            </div>

            <div class="vendor-action">

                <a
                    class="btn-wa"
                    href="https://wa.me/${formatNomor(item.nomor_telepon)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Chat WhatsApp">

                    <i class="fab fa-whatsapp"></i>

                </a>

                ${
                item.email
                ?
                `
                <a
                    class="btn-email"
                    href="https://mail.google.com/mail/?view=cm&to=${encodeURIComponent(item.email)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    title="Kirim Email">

                    <i class="fas fa-envelope"></i>

                </a>
                `
                :
                `
                <button
                    class="btn-email"
                    disabled
                    title="Email tidak tersedia">

                    <i class="fas fa-envelope"></i>

                </button>
                `
                }

                <button
                    class="btn-edit"
                    onclick="editVendor(${item.id})">

                    <i class="fas fa-pen"></i>

                </button>

                <button
                    class="btn-delete"
                    onclick="hapusVendor(${item.id})">

                    <i class="fas fa-trash"></i>

                </button>

            </div>

        </div>

        `;

    });

    container.innerHTML = html;

}

function bukaModalTambah(){

    document
        .getElementById("formVendor")
        .reset();

    document
        .getElementById("vendorId")
        .value="";

    document
        .getElementById("modalVendor")
        .classList.add("show");

}

function tutupModal(){

    document
        .getElementById("modalVendor")
        .classList.remove("show");

}

document.addEventListener("keydown",function(e){

    if(e.key==="Escape"){

        tutupModal();

    }

});

window.onclick=function(e){

    const modal=document.getElementById("modalVendor");

    if(e.target==modal){

        tutupModal();

    }

};

async function simpanVendor(e){

    e.preventDefault();

    const id = document.getElementById("vendorId").value;

    const data = {

        id_vendor_tampilan:
            document.getElementById("id_vendor_tampilan").value,

        nama_vendor:
            document.getElementById("nama_vendor").value,

        barang_disuplai:
            document.getElementById("barang_disuplai").value,

        nomor_telepon:
            document.getElementById("nomor_telepon").value,

        email:
            document.getElementById("email").value,

        status:
            document.getElementById("status").value

    };

    let url = `${API}/vendors`;
    let method = "POST";

    if(id!=""){

        url = `${API}/vendors/${id}`;
        method = "PUT";

    }

    try{

        const res = await fetch(url,{

            method:method,

            credentials:"include",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify(data)

        });

        const result = await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Gagal",
                result.message,
                "error"
            );

            return;

        }

        Swal.fire({

            icon:"success",

            title:"Berhasil",

            text:result.message,

            timer:1500,

            showConfirmButton:false

        });

        tutupModal();

        loadVendor();

    }

    catch(err){

        console.log(err);

        Swal.fire(
            "Error",
            "Terjadi kesalahan.",
            "error"
        );

    }

}

async function editVendor(id){

    try{

        const res = await fetch(`${API}/vendors/${id}`,{

            credentials:"include"

        });

        const result = await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Error",
                result.message,
                "error"
            );

            return;

        }

        const v = result.data;

        document.getElementById("vendorId").value = v.id;

        document.getElementById("id_vendor_tampilan").value = v.id_vendor_tampilan;

        document.getElementById("nama_vendor").value = v.nama_vendor;

        document.getElementById("barang_disuplai").value = v.barang_disuplai;

        document.getElementById("nomor_telepon").value = v.nomor_telepon;

        document.getElementById("email").value = v.email || "";

        document.getElementById("status").value = v.status;

        document
            .getElementById("modalVendor")
            .classList.add("show");

    }

    catch(err){

        console.log(err);

    }

}

async function hapusVendor(id){

    const konfirmasi = await Swal.fire({

        title:"Hapus Vendor?",

        text:"Data tidak dapat dikembalikan.",

        icon:"warning",

        showCancelButton:true,

        confirmButtonText:"Ya",

        cancelButtonText:"Batal"

    });

    if(!konfirmasi.isConfirmed)
        return;

    try{

        const res = await fetch(`${API}/vendors/${id}`,{

            method:"DELETE",

            credentials:"include"

        });

        const result = await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Gagal",
                result.message,
                "error"
            );

            return;

        }

        Swal.fire({

            icon:"success",

            title:"Berhasil",

            text:result.message,

            timer:1500,

            showConfirmButton:false

        });

        loadVendor();

    }

    catch(err){

        console.log(err);

    }

}

function refreshVendor(){

    loadVendor();

}

document.querySelectorAll(".close").forEach(btn=>{

    btn.addEventListener("click",tutupModal);

});

document
.getElementById("modalVendor")
.addEventListener("transitionend",()=>{

    loadVendor();

});

window.addEventListener("click",(e)=>{

    const modal=document.getElementById("modalVendor");

    if(e.target===modal){

        tutupModal();

    }

});

document
.getElementById("searchVendor")
.addEventListener("keyup",function(e){

    if(e.key==="Enter"){

        cariVendor();

    }

});

const tabVendor = document.getElementById("tabVendor");
const tabPO = document.getElementById("tabPO");

const vendorSection = document.getElementById("vendorSection");
const poSection = document.getElementById("poSection");

tabVendor.addEventListener("click", () => {

    tabVendor.classList.add("active");
    tabPO.classList.remove("active");

    vendorSection.style.display = "block";
    poSection.style.display = "none";

});

tabPO.addEventListener("click", () => {

    tabPO.classList.add("active");
    tabVendor.classList.remove("active");

    vendorSection.style.display = "none";
    poSection.style.display = "block";

});
