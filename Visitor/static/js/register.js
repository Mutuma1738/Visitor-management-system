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
        event.preventDefault(); // Prevent default form submission
        const action = submitBtn.getAttribute("data-action");
        const csrfToken = getCSRFToken(); // Get CSRF token

        if (!csrfToken) {
            alert("CSRF token missing! Please refresh the page.");
            return;
        }

        if (action === "register") {
            fetch("/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken // Include CSRF token
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
                    swal("Success!", "Visitor registered successfully!", "success");
                    submitBtn.innerText = "Log Visit";
                    submitBtn.setAttribute("data-action", "log");
                }
            })
            .catch(error => console.error("Error registering visitor:", error));
        } else if (action === "log") {
            let formData = new FormData(form); // Get all form data

            fetch("/log_visit/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken // CSRF token in headers
                },
                body: formData // Send as FormData, not JSON
            })
            .then(response => {
                if (response.ok) {
                    swal("Success!", "Visit logged successfully!", "success")
                        .then(() => window.location.reload());
                } else {
                    return response.json().then(data => { throw new Error(data.error); });
                }
            })
            .catch(error => console.error("Error logging visit:", error));
        }
    });
});
