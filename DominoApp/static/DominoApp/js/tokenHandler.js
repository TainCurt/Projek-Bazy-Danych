const token = localStorage.getItem("authToken");
const response = await fetch("/api/buildings/", {
    headers: {
        "Authorization": "Token " + token // jeśli tak obsługujesz token w utils.py
    }
});