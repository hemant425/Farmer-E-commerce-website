function registerFarmer() {
    let username = document.getElementById("register_username").value.trim();
    let password = document.getElementById("register_password").value.trim();
    let farmName = document.getElementById("register_farm").value.trim();

    if (!username || !password || !farmName) {
        alert("Please fill in all fields.");
        return;
    }

    let farmers = JSON.parse(localStorage.getItem("farmers")) || {};

    if (farmers[username]) {
        alert("Username already exists. Choose a different one.");
        return;
    }

    // Store user details in localStorage
    farmers[username] = { password: password, farm: farmName };
    localStorage.setItem("farmers", JSON.stringify(farmers));

    console.log("Registered farmers:", farmers); // Debugging
    alert("Registration successful! You can now log in.");
}

function loginFarmer() {
    let username = document.getElementById("login_username").value.trim();
    let password = document.getElementById("login_password").value.trim();

    let farmers = JSON.parse(localStorage.getItem("farmers")) || {};
    console.log("Stored farmers:", farmers); // Debugging

    if (farmers[username]) {
        console.log("Stored password:", farmers[username].password);
        console.log("Entered password:", password);
    }

    if (farmers[username] && farmers[username].password === password) {
        alert("Login successful! Welcome, " + username);
    } else {
        alert("Invalid username or password.");
    }
}
