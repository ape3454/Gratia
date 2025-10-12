const menuicon = document.getElementById("5");
const menubutton3 = document.getElementById("3");
const menubutton4 = document.getElementById("4");

const jsoncommunication = document.getElementsByClassName("home")[0].getElementsByClassName("jsoncommunication")[0];
const user = jsoncommunication.textContent.slice(2, self.length - 2).split("', '");


if (sessionStorage.getItem("account") === null) {
    sessionStorage.setItem("account", null);
}
var account = sessionStorage.getItem("account");


if (account == "null") {
    menuicon.href = "/";
    menubutton3.href = "login";
    menubutton4.textContent = "Log In";
    menubutton4.href = "login";
}
else {
    menuicon.href = "home";
    menubutton3.href = "donate";
    menubutton4.textContent = "Profile";
    menubutton4.href = "profile";
}

if ("serviceworker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("static/js/serviceworker.js")
            .then((res) => console.log("service worker registered"))
            .catch((err) => console.log("service worker not registered", err));
    })
}


function storeaccount() {
    if ("email" == "email") {
        email = emailfd.value;
    }
    else if (field == "password") {
        password = passwordfd.value;
    }
}