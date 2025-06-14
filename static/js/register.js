
function toggleContactInput() {
    var contactType = document.getElementById("contact_type").value;
    var contactAccountInput = document.getElementById("contact_account");

    if (contactType === "qq" || contactType === "wechat") {
        contactAccountInput.style.display = "block";
        contactAccountInput.setAttribute("required", "required");
    } else {

        contactAccountInput.style.display = "none";
        contactAccountInput.removeAttribute("required");
        contactAccountInput.value = "";
    }
}


document.addEventListener('DOMContentLoaded', (event) => {
    toggleContactInput();
});