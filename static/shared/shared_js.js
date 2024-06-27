// check sign-in status
function getTokenData() {
    let token = localStorage.getItem("token");
    let auth = "Bearer " + token;
    let p = new Promise(function (resolve) {
        fetch("/api/user/auth", {method: "GET", headers: {"Authorization": auth}}).then(function (response) {
            return response.json();
        }).then(function (data) {
            let tokenData;
            if (data == null) {
                tokenData = null;
            } else if (data.data) {
                tokenData = data.data;
            } else {
                check = null;
            }
            resolve(tokenData);
        })
    })
    return p;
}

function loadSignInPage (callback) {
    document.addEventListener("DOMContentLoaded", function () {
        let navSigninDiv = document.getElementById("nav-signin");
        navSigninDiv.innerHTML = "";
        navSigninDiv.setAttribute("data-status", "false");
        getTokenData().then(function(tokenData) {
            if (tokenData) {
                navSigninDiv.innerHTML = "登出系統";
                navSigninDiv.setAttribute("data-status", "true");
            } else {
                navSigninDiv.innerHTML = "登入/註冊";
                navSigninDiv.setAttribute("data-status", "false");
            }
            callback(tokenData)
        })
    });
}




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
    document.getElementById("signin-msg").style.display = "none";
    document.getElementById("popup-dialog").style.display = "block";
}

// close dialog
function closeDialog() {
    document.getElementById("popup-dialog").style.display = "none";

}

// change to signup
function changeToSignup() {
    document.getElementById("signup-msg").style.display = "none";
    document.getElementById("dialog-signin").style.display = "none";
    document.getElementById("dialog-signup").style.display = "block";
}

// change to signin
function changeToSignin() {
    document.getElementById("signin-msg").style.display = "none";
    document.getElementById("dialog-signin").style.display = "block";
    document.getElementById("dialog-signup").style.display = "none";
}

// sign out procedure
function signOut () {
    localStorage.removeItem("token");
    location.reload();
}



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
function signUp(event) {
    event.preventDefault();
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
function signIn(event) {
    event.preventDefault();
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
    });
}

// booking button
document.getElementById("nav-booking").addEventListener("click", function() {
    // check sign-in status
    getTokenData().then(function (tokenData) {
        if (tokenData) {
            location.href = "/booking";
        } else {
            showSigninDialog();
        }
    });
});