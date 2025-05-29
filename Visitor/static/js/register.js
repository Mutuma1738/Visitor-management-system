// This script handles the visitor registration and logging process.
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");

    const IdInput = document.getElementById("Id_number");
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const mobileInput = document.getElementById("mobile");
    const employeeInput = document.getElementById("employee");
    const purposeInput = document.getElementById("purpose");
    const officialReasonInput = document.getElementById("official_reason");
    const otherReasonInput = document.getElementById("other_reason");
    const checkIdBtn = document.getElementById("check-Id-btn");
    const submitBtn = document.getElementById("submit-btn");
    const form = document.querySelector("form");

    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : null;
    }

    checkIdBtn.addEventListener("click", function () {
        fetch(`/check_visitor/?Id_number=${IdInput.value}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    nameInput.value = data.name;
                    emailInput.value = data.email;
                    mobileInput.value = data.mobile;

                    nameInput.readOnly = true;
                    emailInput.readOnly = true;
                    mobileInput.readOnly = true;

                    submitBtn.innerText = "Log Visit";
                    submitBtn.setAttribute("data-action", "log");
                } else {
                    swal({
                        title: "Warning!",
                        text: data.message,
                        icon: "warning",
                        button: "Okay",
                    });

                    nameInput.readOnly = false;
                    emailInput.readOnly = false;
                    mobileInput.readOnly = false;

                    nameInput.value = "";
                    emailInput.value = "";
                    mobileInput.value = "";

                    submitBtn.innerText = "Register";
                    submitBtn.setAttribute("data-action", "register");
                }
            })
            .catch(error => console.error("Error fetching visitor data:", error));
    });

   
    form.addEventListener("submit", function (event) {
    event.preventDefault();
    const action = submitBtn.getAttribute("data-action");
    const csrfToken = getCSRFToken();

    if (action === "register") {
        fetch("/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                Id_number: IdInput.value,
                name: nameInput.value,
                mobile: mobileInput.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                swal("Error!", data.error, "error");
            } else {
                swal("Success!", "Visitor registered successfully!", "success").then(() => {
                    submitBtn.innerText = "Log Visit";
                    submitBtn.setAttribute("data-action", "log");
                    submitBtn.disabled = false; // Ensure the button is enabled

                });
            }
        })
        .catch(error => console.error("Error registering visitor:", error));
    }
    // ... other code for "log" actionyyy

    else if (action === "log") {
        let formData = new FormData(form);
    
        fetch("/log_visit/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) throw new Error("Request failed");
            return response.json();
        })
        .then(data => {
            if (data.success) {
                swal("Success!", data.message, "success").then(() => {
                    window.location.href = "/";
                });
            } else {
                swal("Error!", data.message || "Unknown error", "error");
            }
        })
        .catch(error => {
            console.error("Log visit error:", error);
            swal("Error!", "Something went wrong while logging the visit.", "error");
        });
    }
    
    });
});
