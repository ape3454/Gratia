const menubutton5 = document.getElementsByClassName("5");
const menubutton3 = document.getElementsByClassName("3");
const menubutton4 = document.getElementsByClassName("4");



const flaskcommunication = document.getElementById("flaskcommunication");
var user = null;
if (flaskcommunication.textContent != '') {
    if (flaskcommunication.textContent != "loggedout") {
        user = flaskcommunication.textContent.slice(2, self.length - 2).split("', '");
        if (!sessionStorage.getItem("account")) {
            sessionStorage.setItem("account", user);
        }
    }
    else {
        sessionStorage.removeItem("account")
    }
}
else {
    if (sessionStorage.getItem("account")) {
        user = sessionStorage.getItem("account").split(",");
    }
}

if (user == null) {
    for (button of menubutton5) {
        button.href = "/";
    }
    for (button of menubutton3) {
        button.href = "login";
    }
    for (button of menubutton4) {
        button.textContent = "Log In";
        button.href = "login";
    }
}
else {
    for (button of menubutton5) {
        button.href = "home";
    }
    for (button of menubutton3) {
        button.href = "donate";
    }
    for (button of menubutton4) {
        button.textContent = "Profile";
        button.href = "profile";
    }
}

if (document.getElementsByClassName("profile").length != 0) {
    updateinputs = Array.from(document.querySelectorAll("input"));
    let i = 0;
    let j = 0;
    for (input of updateinputs) {
        input.placeholder = user[j];
        i++;
        j++;
        if (i == 4 || i == 5) {
            input.placeholder = '';
            if (i == 4) {
                j--;
            }
            continue;
        }
        if (i == 10) {
            if (user[j] == "TRUE") {
                input.checked = 'true';
            }
        }
    }
    document.getElementById("button").addEventListener("click", changePassword);
}


function changePassword() {
    const box = document.getElementsByClassName("bubble password")[0];
    box.classList.toggle('hidden');
}




if ("serviceWorker" in navigator) {
    window.addEventListener("load", function() {
        navigator.serviceWorker
            .register("static/js/serviceworker.js")
            .then((res) => console.log("service worker registered"))
            .catch((err) => console.log("service worker not registered", err));
    })
}