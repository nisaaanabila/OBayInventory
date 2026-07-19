const API_PO = "/api";

let poData = [];
let poFilter = [];
let poVendor = [];
let poBahan = [];


// ======================================
// DOM READY
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    loadPurchaseOrder();

    loadVendorPO();

    document
        .getElementById("searchPO")
        .addEventListener("input", cariPO);

    document
        .getElementById("vendor_id")
        .addEventListener("change", loadBahanVendor);

    document
        .getElementById("btnTambahPO")
        .addEventListener("click", () => {

            resetFormPO();

            bukaModalPO();

        });

});

// ======================================
// LOAD PURCHASE ORDER
// ======================================

async function loadPurchaseOrder(){

    try{

        const res = await fetch(`${API_PO}/purchase-orders`,{

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

        poData = result.data;
        poFilter = [...poData];

        renderPO();

    }

    catch(err){

        console.log(err);

    }

}


// ======================================
// SEARCH
// ======================================

function cariPO(){

    const keyword = document
        .getElementById("searchPO")
        .value
        .toLowerCase();

    poFilter = poData.filter(item=>{

        return(

            item.kode_po
                .toLowerCase()
                .includes(keyword)

            ||

            item.nama_vendor
                .toLowerCase()
                .includes(keyword)

        );

    });

    renderPO();

}


// ======================================
// RENDER TABLE
// ======================================

function renderPO(){

    const tbody =
        document.getElementById("tablePO");

    if(poFilter.length==0){

        tbody.innerHTML=`

            <tr>

                <td colspan="5">

                    Belum ada Purchase Order.

                </td>

            </tr>

        `;

        return;

    }

    let html="";

    poFilter.forEach(item=>{

        html+=`

        <tr>

            <td>

                ${item.kode_po}

            </td>

            <td>

                ${item.nama_vendor}

            </td>

            <td>

                ${item.tanggal}

            </td>

            <td>

                <span class="badge ${item.status.toLowerCase()}">
                    ${item.status}
                </span>

            </td>

            <td>

                <button
                    class="btn-edit"
                    onclick="editPO(${item.id})">

                    <i class="fas fa-pen"></i>

                </button>

                <button
                    class="btn-delete"
                    onclick="hapusPO(${item.id})">

                    <i class="fas fa-trash"></i>

                </button>

                <button
                    class="btn-pdf"
                    onclick="downloadPDF(${item.id})">

                    <i class="fas fa-file-pdf"></i>

                </button>

            </td>

        </tr>

        `;

    });

    tbody.innerHTML = html;

}


// ======================================
// LOAD VENDOR
// ======================================

async function loadVendorPO(){

    try{

        const res = await fetch(`${API_PO}/vendors-po`,{

            credentials:"include"

        });

        const result = await res.json();

        if(result.status!="success")
            return;

        poVendor = result.data;

        let option = `

            <option value="">

                Pilih Vendor

            </option>

        `;

        poVendor.forEach(v=>{

            option += `

                <option value="${v.id}">

                    ${v.nama_vendor}

                </option>

            `;

        });

        document
            .getElementById("vendor_id")
            .innerHTML = option;

    }

    catch(err){

        console.log(err);

    }

}


// ======================================
// BUKA MODAL
// ======================================

function bukaModalPO(){

    document
        .getElementById("modalPO")
        .classList.add("show");

}


// ======================================
// TUTUP MODAL
// ======================================

function tutupModalPO(){

    document
        .getElementById("modalPO")
        .classList.remove("show");

}


// ======================================
// RESET FORM
// ======================================

function resetFormPO(){

    document
        .getElementById("poId")
        .value="";

    document
        .getElementById("vendor_id")
        .value="";

    document
        .getElementById("tanggal")
        .value="";

    document
        .getElementById("estimasi")
        .value="";

    document
        .getElementById("catatan")
        .value="";

    document
        .getElementById("detailBody")
        .innerHTML="";
    const total = document.getElementById("grandTotal");

if(total){
    total.remove();
}

}


// ======================================
// ESC CLOSE
// ======================================

document.addEventListener("keydown",(e)=>{

    if(e.key==="Escape"){

        tutupModalPO();

    }

});


// ======================================
// CLICK OUTSIDE MODAL
// ======================================

window.addEventListener("click",(e)=>{

    const modal =
        document.getElementById("modalPO");

    if(e.target===modal){

        tutupModalPO();

    }

});

// ======================================
// LOAD BAHAN BERDASARKAN VENDOR
// ======================================

async function loadBahanVendor(){

    const vendorId =
        document.getElementById("vendor_id").value;

    document
        .getElementById("detailBody")
        .innerHTML = "";

    if(vendorId==""){

        poBahan=[];

        return;

    }

    try{

        const res = await fetch(

            `${API_PO}/vendors-po/${vendorId}/bahan`,

            {

                credentials:"include"

            }

        );

        const result = await res.json();

        if(result.status!="success"){

            Swal.fire(

                "Error",

                result.message,

                "error"

            );

            return;

        }

        poBahan=result.data;

    }

    catch(err){

        console.log(err);

    }

}



// ======================================
// TAMBAH BARIS BAHAN
// ======================================

function tambahBarisBahan(){

    if(poBahan.length==0){

        Swal.fire(

            "Pilih Vendor",

            "Silakan pilih vendor terlebih dahulu.",

            "warning"

        );

        return;

    }

    let option="";

    poBahan.forEach(item=>{

        option+=`

            <option value="${item.id}">

                ${item.nama_bahan}

            </option>

        `;

    });

    const tbody=document.getElementById("detailBody");

    tbody.insertAdjacentHTML(

        "beforeend",

        `

        <tr>

            <td>

                <select class="bahan">

                    ${option}

                </select>

            </td>

            <td>

                <input

                    type="number"

                    class="qty"

                    min="1"

                    value="1"

                    oninput="hitungSubtotal(this)">

            </td>

            <td>

                <input

                    type="number"

                    class="harga"

                    min="0"

                    value="0"

                    oninput="hitungSubtotal(this)">

            </td>

            <td class="subtotal">

                Rp 0

            </td>

            <td>

                <button

                    class="btn-delete"

                    onclick="hapusBaris(this)">

                    <i class="fas fa-trash"></i>

                </button>

            </td>

        </tr>

        `

    );

    hitungTotal();

}



// ======================================
// HAPUS BARIS
// ======================================

function hapusBaris(btn){

    btn.closest("tr").remove();

    hitungTotal();

}



// ======================================
// HITUNG SUBTOTAL
// ======================================

function hitungSubtotal(element){

    const row = element.closest("tr");

    const qty = parseFloat(

        row.querySelector(".qty").value

    ) || 0;

    const harga = parseFloat(

        row.querySelector(".harga").value

    ) || 0;

    const subtotal = qty * harga;

    row.querySelector(".subtotal").innerHTML =

        "Rp " +

        subtotal.toLocaleString("id-ID");

    hitungTotal();

}



// ======================================
// HITUNG TOTAL PURCHASE ORDER
// ======================================

function hitungTotal(){

    let total = 0;

    document

        .querySelectorAll("#detailBody tr")

        .forEach(row=>{

            const qty = parseFloat(

                row.querySelector(".qty").value

            ) || 0;

            const harga = parseFloat(

                row.querySelector(".harga").value

            ) || 0;

            total += qty * harga;

        });

    let totalElement =

        document.getElementById("grandTotal");

    if(!totalElement){

        totalElement=document.createElement("div");

        totalElement.id="grandTotal";

        totalElement.style.marginTop="15px";

        totalElement.style.fontWeight="bold";

            document
            .querySelector("#modalPO .modal-content")
            .appendChild(totalElement);

    }

    totalElement.innerHTML =

        "TOTAL : Rp " +

        total.toLocaleString("id-ID");

}



// ======================================
// AMBIL DETAIL UNTUK DIKIRIM KE API_PO
// ======================================

function ambilDetailPO(){

    const detail=[];

    document

        .querySelectorAll("#detailBody tr")

        .forEach(row=>{

            detail.push({

                bahan_id:

                    row.querySelector(".bahan").value,

                qty:

                    row.querySelector(".qty").value,

                harga:

                    row.querySelector(".harga").value

            });

        });

    return detail;

}

// ======================================
// SIMPAN PURCHASE ORDER
// ======================================

async function simpanPO(){

    const id = document.getElementById("poId").value;

    const detail = ambilDetailPO();

    if(detail.length===0){

        Swal.fire(
            "Peringatan",
            "Tambahkan minimal satu bahan.",
            "warning"
        );

        return;

    }

    const data={

        vendor_id:
            document.getElementById("vendor_id").value,

        tanggal:
            document.getElementById("tanggal").value,

        estimasi_pengiriman:
            document.getElementById("estimasi").value,

        catatan:
            document.getElementById("catatan").value,

        detail:detail

    };

    let url=`${API_PO}/purchase-orders`;
    let method="POST";

    if(id!=""){

        url=`${API_PO}/purchase-orders/${id}`;
        method="PUT";

    }

    try{

        const res=await fetch(url,{

            method:method,

            credentials:"include",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify(data)

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

        Swal.fire({

            icon:"success",

            title:"Berhasil",

            text:result.message,

            timer:1500,

            showConfirmButton:false

        });

        tutupModalPO();

        loadPurchaseOrder();

    }

    catch(err){

        console.log(err);

    }

}
// ======================================
// TAB MENU
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    const tabVendor = document.getElementById("tabVendor");
    const tabPO = document.getElementById("tabPO");

    const vendorSection = document.getElementById("vendorSection");
    const poSection = document.getElementById("poSection");

    tabVendor.onclick = () => {

        vendorSection.style.display = "block";
        poSection.style.display = "none";

        tabVendor.classList.add("active");
        tabPO.classList.remove("active");

    };

    tabPO.onclick = () => {

        vendorSection.style.display = "none";
        poSection.style.display = "block";

        tabPO.classList.add("active");
        tabVendor.classList.remove("active");

        loadPurchaseOrder();

    };

});
// ======================================
// DOWNLOAD PDF PURCHASE ORDER
// ======================================

function downloadPDF(id){

    window.location.href =
        `${API_PO}/purchase-orders/${id}/pdf`;

}