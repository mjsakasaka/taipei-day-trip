// link on website title
document.getElementById("nav-title").addEventListener("click", function() {
    window.location.href = "/";
});

// load popup-dialog
document.addEventListener('DOMContentLoaded', function() {
    fetch('/static/shared/popup_dialog.html')
    .then(response => response.text())
    .then(data => {
        document.getElementById('popup-dialog').innerHTML = data;
    })
    .catch(error => console.error('Error loading shared content:', error));
});


// show dialog
function showSigninDialog() {
    document.getElementById("dialog-mask").style.display = "block";
    document.getElementById("dialog-signin").style.display = "block";
}

// close dialog
function closeDialog() {
    document.getElementById("dialog-mask").style.display = "none";
    document.getElementById("dialog-signin").style.display = "none";
    document.getElementById("dialog-signup").style.display = "none";
}

// change to signup
function changeToSignup() {
    document.getElementById("dialog-signin").style.display = "none";
    document.getElementById("dialog-signup").style.display = "block";
}

// change to signin
function changeToSignin() {
    document.getElementById("dialog-signin").style.display = "block";
    document.getElementById("dialog-signup").style.display = "none";
}

// sign out procedure
function signOut () {
    localStorage.removeItem("token");
    location.reload();
}

// check sign-in status
let auth = "Bearer " + localStorage.getItem("token");
fetch("/api/user/auth", {method: "GET", headers: {"Authorization": auth}}).then(function (response) {
    return response.json();
}).then(function (data) {
    if (data != null) {
        let navSigninDiv = document.getElementById("nav-signin");
        navSigninDiv.innerHTML = "登出系統";
        navSigninDiv.setAttribute("data-status", "true");
    } else {
        let navSigninDiv = document.getElementById("nav-signin");
        navSigninDiv.innerHTML = "登入/註冊";
        navSigninDiv.setAttribute("data-status", "false");
    }
})

// sign-in/sign-out button
document.getElementById("nav-signin").addEventListener("click", function () {
    let status = document.getElementById("nav-signin").getAttribute("data-status");
    if (status == "false") {
        showSigninDialog();
    } else if (status == "true") {
        signOut();
    }
});

// sign up procedure
function signUp () {
    let name = document.getElementById("signup-name").value;
    let email = document.getElementById("signup-email").value;
    let password = document.getElementById("signup-pwd").value;
    let bodyData = {"name": name, "email": email, "password": password};
    fetch("/api/user", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(bodyData)}).then(function (response) {
        return response.json();
    }).then(function (data) {
        if (data.ok) {
            let msgDiv = document.getElementById("signup-msg");
            msgDiv.style.display = "block";
            msgDiv.style.color = "#666666";
            msgDiv.innerHTML = "註冊成功";
        } else if (data.error) {
            let msgDiv = document.getElementById("signup-msg");
            msgDiv.style.display = "block";
            msgDiv.style.color = "red";
            msgDiv.innerHTML = "註冊失敗，重複的 Email 或其他原因";
        }
    });
}

// sign in procedure
function signIn () {
let email = document.getElementById("signin-email").value;
let password = document.getElementById("signin-pwd").value;
let bodyData = {"email": email, "password": password};
fetch("/api/user/auth", {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(bodyData)}).then(function (response) {
    return response.json();
}).then(function (data) {
    if (data.token) {
        localStorage.setItem("token", data.token);
        location.reload();
    } else if (data.error) {
        let msgDiv = document.getElementById("signin-msg");
        msgDiv.style.display = "block";
        msgDiv.style.color = "red";
        msgDiv.innerHTML = "賬號或密碼錯誤";
    }
})
}