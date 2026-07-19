document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

async function loadDashboard() {

    try {

        const response = await fetch("/api/dashboard", {
            method: "GET",
            credentials: "include"
        });

        const result = await response.json();

        console.log(result);

        if (result.status !== "success") {
            alert(result.message);
            return;
        }

        // ==========================
        // SUMMARY
        // ==========================

        document.getElementById("totalBahan").textContent =
            result.summary.total_bahan;

        document.getElementById("totalProduk").textContent =
            result.summary.total_produk;

        document.getElementById("totalVendor").textContent =
            result.summary.total_vendor;

        document.getElementById("stokMenipis").textContent =
            result.summary.stok_menipis;

        // ==========================
        // TABLE STOK KRITIS
        // ==========================

        const tbody = document.getElementById("criticalTable");

        tbody.innerHTML = "";

        if (!result.critical_inventory ||
            result.critical_inventory.length === 0) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align:center">
                        Tidak ada stok kritis
                    </td>
                </tr>
            `;

            return;
        }

        result.critical_inventory.forEach(item => {

            let badge = "";

            if (item.status === "KRITIS") {

                badge = `<span class="badge badge-danger">KRITIS</span>`;

            } else if (item.status === "MENIPIS") {

                badge = `<span class="badge badge-warning">MENIPIS</span>`;

            } else {

                badge = `<span class="badge badge-success">AMAN</span>`;
            }

            tbody.innerHTML += `
                <tr>
                    <td>${item.nama_bahan}</td>
                    <td>${item.stok_saat_ini}</td>
                    <td>${item.minimum_stok}</td>
                    <td>${badge}</td>
                </tr>
            `;

        });

    }

    catch (err) {

        console.error(err);

        alert("Gagal mengambil data dashboard.");

    }

}