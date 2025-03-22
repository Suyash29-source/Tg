import os
import threading
import requests
import json
from flask import Flask, request, redirect, session, render_template
import config  # ✅ Import config file

# ✅ Use config values directly
BOT_TOKEN = config.BOT_TOKEN
APP_URL = config.APP_URL
CHANNEL_USERNAME = config.CHANNEL_USERNAME
TELEGRAM_BOT_USERNAME = config.TELEGRAM_BOT_USERNAME

# ✅ Initialize Flask App
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ✅ Telegram OAuth Login URL
TELEGRAM_AUTH_URL = f"https://oauth.telegram.org/auth?bot_id={BOT_TOKEN.split(':')[0]}&origin={APP_URL}&return_to={APP_URL}/login"

# ✅ Run `chatbook.py` (Telegram Bot in Background)
def run_telegram_bot():
    os.system("python chatbook.py")  # Pydroid ke liye "python" likhna hoga

# ✅ Homepage (Login Page)
@app.route("/")
def home():
    return render_template("index.html", telegram_auth_url=TELEGRAM_AUTH_URL)

# ✅ Telegram OAuth Redirect (Login User)
@app.route("/login")
def login():
    if "hash" not in request.args:
        return "Invalid Telegram Login!", 400
    
    user_data = {
        "id": request.args.get("id"),
        "first_name": request.args.get("first_name"),
        "last_name": request.args.get("last_name", ""),
        "username": request.args.get("username", ""),
        "photo_url": request.args.get("photo_url", "")
    }

    user_id = user_data["id"]

    # ✅ Check If User Is in Channel
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={user_id}")
    data = response.json()
    if "status" not in data.get("result", {}) or data["result"]["status"] not in ["member", "administrator", "creator"]:
        return "⚠️ You must join our Telegram channel first!", 403

    # ✅ Save User in Session
    session["user"] = user_data
    return redirect("/dashboard")

# ✅ Dashboard (After Login)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    
    user = session["user"]
    return render_template("dashboard.html", user=user)

# ✅ Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ✅ Start Flask App & Telegram Bot in Pydroid
if __name__ == "__main__":
    t1 = threading.Thread(target=run_telegram_bot)
    t1.start()
    app.run(host="0.0.0.0", port=5000, debug=True)  # Pydroid me 5000 port use hoga