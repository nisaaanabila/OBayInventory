const API = "/api";

let dataProduk = [];
let dataFilter = [];
let dataBahan = [];
let resepAktif = [];

let selectedProduk = null;

// ======================================
// DOM READY
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    loadProduk();
    loadBahan();

    document
        .getElementById("searchProduk")
        .addEventListener("input", cariProduk);

    // OWNER ONLY
    if (ROLE === "OWNER") {

        document
            .getElementById("btnTambahProduk")
            .addEventListener("click", bukaModalTambah);

        document
            .getElementById("formProduk")
            .addEventListener("submit", simpanProduk);

        document
            .getElementById("btnTambahResep")
            .addEventListener("click", bukaModalResep);

        document
            .getElementById("formResep")
            .addEventListener("submit", simpanResep);

    }

});

// ======================================
// LOAD PRODUK
// ======================================

async function loadProduk(){

    try{

        const res = await fetch(`${API}/produk`,{

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

        dataProduk = result.data;
        dataFilter = [...dataProduk];

        renderProduk();

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// LOAD BAHAN
// ======================================

async function loadBahan(){

    try{

        const res = await fetch(`${API}/bahan`,{

            credentials:"include"

        });

        const result = await res.json();

        if(result.status=="success"){

            dataBahan = result.data;

        }

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// SEARCH
// ======================================

function cariProduk(){

    const keyword = document
        .getElementById("searchProduk")
        .value
        .toLowerCase();

    dataFilter = dataProduk.filter(item =>

        item.nama_produk.toLowerCase().includes(keyword)
        ||
        item.kode_produk.toLowerCase().includes(keyword)

    );

    renderProduk();

}

// ======================================
// RENDER PRODUK
// ======================================

function renderProduk(){

    const container =
    document.getElementById("listProduk");

    if(dataFilter.length===0){

        container.innerHTML=`

            <div class="empty">

                Belum ada produk.

            </div>

        `;

        return;

    }

    let html="";

    dataFilter.forEach(item=>{

        html += `

        <div
            class="product-card"
            onclick="pilihProduk(${item.id})">

            <img
                src="${item.gambar_url || '/static/img/no-image.png'}">

            <div class="product-info">

                <h3>${item.nama_produk}</h3>

                <small>${item.kode_produk}</small>

                <p>${item.kategori}</p>

                <span>

                    Rp ${Number(item.harga).toLocaleString("id-ID")}

                </span>

            </div>

            ${
                ROLE==="OWNER"
                ?

                `

                <div class="aksi">

                    <button
                    onclick="event.stopPropagation();editProduk(${item.id})">

                        <i class="fas fa-edit"></i>

                    </button>

                    <button
                    onclick="event.stopPropagation();hapusProduk(${item.id})">

                        <i class="fas fa-trash"></i>

                    </button>

                </div>

                `

                :

                ""

            }

        </div>

        `;

    });

    container.innerHTML = html;

}

// ======================================
// PILIH PRODUK
// ======================================

function pilihProduk(id){

    selectedProduk = id;

    const produk = dataProduk.find(item=>item.id==id);

    if(!produk)
        return;

    document.getElementById("gambarProduk").src =
        produk.gambar_url || "/static/img/no-image.png";

    document.getElementById("namaProduk").innerHTML =
        produk.nama_produk;

    document.getElementById("kategoriProduk").innerHTML =
        produk.kategori;

    document.getElementById("hargaProduk").innerHTML =
        "Rp " + Number(produk.harga).toLocaleString("id-ID");

    document.getElementById("statusProduk").innerHTML =
        produk.status;

    if(ROLE==="OWNER"){

        document
        .getElementById("btnEditProduk")
        .onclick=()=>editProduk(id);

        document
        .getElementById("btnDeleteProduk")
        .onclick=()=>hapusProduk(id);

    }

    loadResep(id);

}
// ======================================
// BUKA MODAL TAMBAH PRODUK
// ======================================

function bukaModalTambah(){

    document.getElementById("formProduk").reset();

    document.getElementById("produkId").value="";

    document.getElementById("status").value="Aktif";

    document
        .getElementById("modalProduk")
        .classList.add("show");

}

// ======================================
// TUTUP MODAL PRODUK
// ======================================

function tutupModal(){

    document
        .getElementById("modalProduk")
        .classList.remove("show");

}

// ======================================
// SIMPAN PRODUK
// ======================================

async function simpanProduk(e){

    e.preventDefault();

    const id=document.getElementById("produkId").value;

    const data={

        kode_produk:
            document.getElementById("kode_produk").value,

        nama_produk:
            document.getElementById("nama_produk").value,

        kategori:
            document.getElementById("kategori").value,

        harga:
            document.getElementById("harga").value,

        gambar_url:
            document.getElementById("gambar_url").value,

        status:
            document.getElementById("status").value

    };

    let url=`${API}/produk`;
    let method="POST";

    if(id!=""){

        url=`${API}/produk/${id}`;
        method="PUT";

    }

    try{

        const res=await fetch(url,{

            method,

            credentials:"include",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)

        });

        const result=await res.json();

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

        await loadProduk();

        if(selectedProduk){

            pilihProduk(selectedProduk);

        }

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

// ======================================
// EDIT PRODUK
// ======================================

async function editProduk(id){

    try{

        const res=await fetch(`${API}/produk/${id}`,{

            credentials:"include"

        });

        const result=await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Error",
                result.message,
                "error"
            );

            return;

        }

        const p=result.data;

        document.getElementById("produkId").value=p.id;

        document.getElementById("kode_produk").value=p.kode_produk;

        document.getElementById("nama_produk").value=p.nama_produk;

        document.getElementById("kategori").value=p.kategori;

        document.getElementById("harga").value=p.harga;

        document.getElementById("gambar_url").value=p.gambar_url || "";

        document.getElementById("status").value=p.status;

        document
            .getElementById("modalProduk")
            .classList.add("show");

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// HAPUS PRODUK
// ======================================

async function hapusProduk(id){

    const konfirmasi=await Swal.fire({

        title:"Hapus Produk?",

        text:"Data tidak dapat dikembalikan.",

        icon:"warning",

        showCancelButton:true,

        confirmButtonText:"Ya",

        cancelButtonText:"Batal"

    });

    if(!konfirmasi.isConfirmed)
        return;

    try{

        const res=await fetch(`${API}/produk/${id}`,{

            method:"DELETE",

            credentials:"include"

        });

        const result=await res.json();

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

        selectedProduk=null;

        document.getElementById("gambarProduk").src=
            "/static/img/no-image.png";

        document.getElementById("namaProduk").innerHTML=
            "Pilih Produk";

        document.getElementById("kategoriProduk").innerHTML="";

        document.getElementById("hargaProduk").innerHTML="";

        document.getElementById("statusProduk").innerHTML="";

        document.getElementById("resepList").innerHTML=`

            <tr>

                <td colspan="${ROLE==="OWNER" ? 4 : 3}"
                    style="text-align:center;padding:30px;">

                    Pilih produk terlebih dahulu.

                </td>

            </tr>

        `;

        loadProduk();

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// REFRESH
// ======================================

function refreshProduk(){

    loadProduk();

}

// ======================================
// CLOSE MODAL
// ======================================

window.onclick=function(e){

    if(
        ROLE==="OWNER"
        &&
        e.target==
        document.getElementById("modalProduk")
    ){

        tutupModal();

    }

}

// ======================================
// ESC
// ======================================

document.addEventListener("keydown",function(e){

    if(
        ROLE==="OWNER"
        &&
        e.key==="Escape"
    ){

        tutupModal();

        tutupModalResep();

    }

});
// ======================================
// LOAD RESEP
// ======================================

async function loadResep(produkId){

    try{

        const res = await fetch(`${API}/resep/${produkId}`,{
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

        resepAktif = result.data;

        renderResep();

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// RENDER RESEP
// ======================================

function renderResep(){

    const tbody=document.getElementById("resepList");

    if(resepAktif.length==0){

        tbody.innerHTML=`

            <tr>

                <td colspan="${ROLE=="OWNER"?4:3}"
                    style="text-align:center;padding:30px;">

                    Belum ada resep.

                </td>

            </tr>

        `;

        return;

    }

    let html="";

    resepAktif.forEach(item=>{

        html+=`

        <tr>

            <td>${item.nama_bahan}</td>

            <td>${item.takaran}</td>

            <td>${item.satuan}</td>

            ${
                ROLE=="OWNER"
                ?

                `<td>

                    <button
                        class="btn-danger"
                        onclick="hapusResep(${item.id})">

                        <i class="fas fa-trash"></i>

                    </button>

                </td>`

                :

                ``

            }

        </tr>

        `;

    });

    tbody.innerHTML=html;

}

// ======================================
// MODAL TAMBAH RESEP
// ======================================

function bukaModalResep(){

    if(ROLE!="OWNER") return;

    if(selectedProduk==null){

        Swal.fire(
            "Pilih Produk",
            "Silakan pilih produk terlebih dahulu.",
            "warning"
        );

        return;

    }

    document.getElementById("formResep").reset();

    let option="";

    dataBahan.forEach(item=>{

        option+=`

            <option value="${item.id}">

                ${item.nama_bahan}

            </option>

        `;

    });

    document.getElementById("bahanResep").innerHTML=option;

    document
        .getElementById("modalResep")
        .classList.add("show");

}

// ======================================
// SIMPAN RESEP
// ======================================

async function simpanResep(e){

    e.preventDefault();

    if(ROLE!="OWNER") return;

    const data={

        produk_id:selectedProduk,

        bahan_id:
            document.getElementById("bahanResep").value,

        takaran:
            document.getElementById("takaran").value

    };

    try{

        const res=await fetch(`${API}/resep`,{

            method:"POST",

            credentials:"include",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)

        });

        const result=await res.json();

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

            timer:1200,

            showConfirmButton:false

        });

        document
            .getElementById("modalResep")
            .classList.remove("show");

        loadResep(selectedProduk);

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// HAPUS RESEP
// ======================================

async function hapusResep(id){

    if(ROLE!="OWNER") return;

    const konfirmasi=await Swal.fire({

        title:"Hapus Bahan?",

        icon:"warning",

        showCancelButton:true,

        confirmButtonText:"Ya",

        cancelButtonText:"Batal"

    });

    if(!konfirmasi.isConfirmed)
        return;

    try{

        const res=await fetch(`${API}/resep/${id}`,{

            method:"DELETE",

            credentials:"include"

        });

        const result=await res.json();

        if(result.status!="success"){

            Swal.fire(
                "Error",
                result.message,
                "error"
            );

            return;

        }

        loadResep(selectedProduk);

    }

    catch(err){

        console.log(err);

    }

}

// ======================================
// TUTUP MODAL RESEP
// ======================================

function tutupModalResep(){

    document
        .getElementById("modalResep")
        .classList.remove("show");

}

// ======================================
// EVENT LISTENER OWNER
// ======================================

if(ROLE=="OWNER"){

    document
    .getElementById("btnTambahResep")
    ?.addEventListener("click",bukaModalResep);

    document
    .getElementById("formResep")
    ?.addEventListener("submit",simpanResep);

}

document
.getElementById("modalResep")
?.addEventListener("hidden.bs.modal",tutupModalResep);
// ======================================
// BUKA MODAL TAMBAH PRODUK
// ======================================

function bukaModalTambah(){

    document.getElementById("formProduk").reset();

    document.getElementById("produkId").value="";

    document
        .getElementById("modalProduk")
        .classList.add("show");

}

// ======================================
// TUTUP MODAL PRODUK
// ======================================

function tutupModal(){

    document
        .getElementById("modalProduk")
        .classList.remove("show");

}

// ======================================
// CLOSE BUTTON
// ======================================

document.querySelectorAll(".close").forEach(btn=>{

    btn.onclick=function(){

        this.closest(".modal")
            .classList.remove("show");

    }

});

// ======================================
// CLICK OUTSIDE
// ======================================

window.onclick=function(e){

    document.querySelectorAll(".modal").forEach(modal=>{

        if(e.target===modal){

            modal.classList.remove("show");

        }

    });

}

// ======================================
// ESC
// ======================================

document.addEventListener("keydown",function(e){

    if(e.key==="Escape"){

        document.querySelectorAll(".modal").forEach(modal=>{

            modal.classList.remove("show");

        });

    }

});

// ======================================
// TUTUP MODAL RESEP
// ======================================

function tutupModalResep(){

    document
        .getElementById("modalResep")
        .classList.remove("show");

}

// ======================================
// EVENT OWNER
// ======================================

if(ROLE==="OWNER"){

    document
        .getElementById("btnTambahResep")
        ?.addEventListener("click",bukaModalResep);

    document
        .getElementById("formResep")
        .addEventListener("submit",simpanResep);

}