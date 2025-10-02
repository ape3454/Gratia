const menubutton3 = document.getElementById("3");
const menubutton4 = document.getElementById("4");

const email = document.getElementById("email")
const email = document.getElementById("password")
const userdb = sqlite3.Database("/database/data_source.db")

if (sessionStorage.getItem("account") === null) {
    sessionStorage.setItem("account", null);
}
var account = sessionStorage.getItem("account");

if (account == "null") {
    menubutton3.href = "signin";
    menubutton4.textContent = "Sign In";
    menubutton4.href = "signin";
}
else {
    menubutton3.href = "donate";
    menubutton4.textContent = "Profile";
    menubutton4.href = "profile";
}

