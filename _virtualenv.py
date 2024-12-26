from flask import Flask, render_template, request, redirect, session
import pyotp
import qrcode
import io
from base64 import b64encode

app = Flask(__name__)
app.secret_key = "secret_key"

# Simulated user database
users = {
    "dorismuna44@gmail.com": {
        "password": "password123",
        "otp_secret": pyotp.random_base32()
    }
}

@app.route('/')
def home():
    return "Welcome to the 2FA Web Application! Go to /login to begin."

# Login Page
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect("/2fa")
        else:
            return "Invalid credentials. Please try again."

    return '''
        <form method="POST">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/2fa', methods=["GET", "POST"])
def two_factor_auth():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    user = users[username]
    otp_secret = user["otp_secret"]

    if request.method == "POST":
        token = request.form["token"]
        totp = pyotp.TOTP(otp_secret)
        if totp.verify(token):
            return "Login successful!"
        else:
            return "Invalid 2FA token. Please try again."

    totp = pyotp.TOTP(otp_secret)
    uri = totp.provisioning_uri(username, issuer_name="My 2FA App")

    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    qr_code_base64 = b64encode(buf.getvalue()).decode("utf-8")

    return f'''
        <p>Scan this QR code with your authenticator app:</p>
        <img src="data:image/png;base64,{qr_code_base64}">
        <form method="POST">
            Enter 2FA Token: <input type="text" name="token"><br>
            <button type="submit">Verify</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
