const menubutton4 = document.querySelector("a #4");

function checkAccount(button) {
    if (button.target.textcontent == "Sign In") {
        button.target.href = "signin";
    }
}

menubutton4.addEventListener("click", checkAccount);