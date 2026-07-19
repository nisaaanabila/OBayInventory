const API = "/api/login";

const form = document.getElementById("loginForm");
const googleBtn = document.querySelector(".google-login");

// ============================================
// LOGIN MANUAL
// ============================================

if (form) {

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (email === "" || password === "") {

            alert("Email / Username dan Password wajib diisi.");
            return;

        }

        const button = document.querySelector(".login-btn");

        if (button) {

            button.disabled = true;

            button.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Login...
            `;

        }

        try {

            const response = await fetch(API, {

                method: "POST",

                credentials: "include",

                headers: {

                    "Content-Type": "application/json"

                },

                body: JSON.stringify({

                    email: email,
                    password: password

                })

            });

            // ===========================
            // DEBUG
            // ===========================

            console.log("STATUS HTTP :", response.status);

            const result = await response.json();

            console.log("HASIL LOGIN :", result);

            // ===========================

                if (response.ok && result.status === "success") {

                    console.log("ROLE :", result.role);

                    // Semua user masuk ke dashboard yang sama
                    window.location.href = "/dashboard";

                }
            else {

                alert(result.message);

                if (button) {

                    button.disabled = false;

                    button.innerHTML = `
                        <i class="fa-solid fa-right-to-bracket"></i>
                        Login
                    `;

                }

            }

        }

        catch (error) {

            console.error("LOGIN ERROR :", error);

            alert("Gagal terhubung ke server.");

            if (button) {

                button.disabled = false;

                button.innerHTML = `
                    <i class="fa-solid fa-right-to-bracket"></i>
                    Login
                `;

            }

        }

    });

}


// ============================================
// LOGIN GOOGLE
// ============================================

if (googleBtn) {

    googleBtn.addEventListener("click", function () {

        window.location.href = "/api/google/login";

    });

}