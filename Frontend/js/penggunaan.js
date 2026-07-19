const API_PENGGUNAAN = `${API}/penggunaan`;
const API_PRODUK = `${API}/produk`;

const penggunaanTable = document.getElementById("penggunaanTable");
const produkSelect = document.getElementById("produk");
const penggunaanForm = document.getElementById("penggunaanForm");

const modal = document.getElementById("detailModal");
const detailBody = document.getElementById("detailBody");
const closeModal = document.getElementById("closeModal");

const search = document.getElementById("searchPenggunaan");


// ============================
// LOAD PRODUK
// ============================

async function loadProduk(){

    try{

        const res = await fetch(API_PRODUK,{
            credentials:"include"
        });

        const result = await res.json();

        produkSelect.innerHTML = `
            <option value="">Pilih Produk</option>
        `;

        result.data.forEach(item=>{

            produkSelect.innerHTML += `
                <option value="${item.id}">
                    ${item.nama_produk}
                </option>
            `;

        });

    }catch(err){

        console.error(err);

    }

}


// ============================
// LOAD PENGGUNAAN
// ============================

async function loadPenggunaan(){

    try{

        const res = await fetch(API_PENGGUNAAN,{
            credentials:"include"
        });

        const result = await res.json();

        penggunaanTable.innerHTML = "";

        result.data.forEach((item,index)=>{

            const tanggal = new Date(item.tanggal)
                .toLocaleString("id-ID");

            penggunaanTable.innerHTML += `

                <tr>

                    <td>${index+1}</td>

                    <td>${tanggal}</td>

                    <td>${item.nama_produk}</td>

                    <td>${item.qty_terjual}</td>

                    <td>${item.nama_user}</td>

                    <td>

                        <button
                            class="detail-btn"
                            onclick="detailPenggunaan(${item.id})">

                            <i class="fa-solid fa-eye"></i>

                            Detail

                        </button>

                    </td>

                </tr>

            `;

        });

    }catch(err){

        console.error(err);

    }

}


// ============================
// SIMPAN
// ============================

penggunaanForm.addEventListener("submit",async(e)=>{

    e.preventDefault();

    const data={

        produk_id:produkSelect.value,

        qty_terjual:document.getElementById("qty").value

    };

    try{

        const res = await fetch(API_PENGGUNAAN,{

            method:"POST",

            credentials:"include",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)

        });

        const result = await res.json();

        alert(result.message);

        if(result.status=="success"){

            penggunaanForm.reset();

            loadPenggunaan();

        }

    }catch(err){

        console.error(err);

    }

});


// ============================
// DETAIL
// ============================

async function detailPenggunaan(id){

    try{

        const res = await fetch(`${API_PENGGUNAAN}/${id}`,{

            credentials:"include"

        });

        const result = await res.json();

        detailBody.innerHTML = "";

        result.data.forEach(item=>{

            detailBody.innerHTML += `

                <tr>

                    <td>${item.nama_bahan}</td>

                    <td>${item.qty_awal}</td>

                    <td>${item.qty_digunakan}</td>

                    <td>${item.qty_sisa}</td>

                </tr>

            `;

        });

        modal.classList.add("active");

    }catch(err){

        console.error(err);

    }

}


// ============================
// CLOSE MODAL
// ============================

closeModal.onclick=()=>{

    modal.classList.remove("active");

}

window.onclick=(e)=>{

    if(e.target==modal){

        modal.classList.remove("active");

    }

}


// ============================
// SEARCH
// ============================

search.addEventListener("keyup",()=>{

    const keyword = search.value.toLowerCase();

    const rows = document.querySelectorAll("#penggunaanTable tr");

    rows.forEach(row=>{

        row.style.display = row.innerText
            .toLowerCase()
            .includes(keyword)

            ? ""

            : "none";

    });

});


// ============================
// INIT
// ============================

loadProduk();

loadPenggunaan();