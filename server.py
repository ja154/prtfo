import os, json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "false").lower() == "true",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
)
print("MAIL_DEFAULT_SENDER =", app.config.get("MAIL_DEFAULT_SENDER"))
print("MAIL_USERNAME       =", app.config.get("MAIL_USERNAME"))

mail = Mail(app)
RECIPIENT = "jmwanguwe3@gmail.com"
LOG_PATH = Path("messages.log")

def write_to_file(data: dict):
    data["timestamp_utc"] = datetime.utcnow().isoformat(timespec="seconds")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

@app.route("/")
def my_home():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send_email():
    name    = request.form.get("name")
    email   = request.form.get("email")
    message = request.form.get("message")

    if not all([name, email, message]):
        flash("Please fill in every field.", "danger")
        return redirect(url_for("my_home") + "#section_5")

    write_to_file({"name": name, "email": email, "message": message})

    msg = Message(
        subject   = f"Portfolio Contact | {name}",
        sender    = "jmwanguwe3@gmail.com",
        recipients = [RECIPIENT],
        reply_to  = email,
        body      = f"Name: {name}\nEmail: {email}\n\n{message}"
    )
    try:
        mail.send(msg)
        flash("Thanks! Your message has been sent ✔", "success")
    except Exception as exc:
        print("Email error:", exc)
        flash("Saved locally but e‑mail failed; we’ll review ASAP.", "warning")

    return redirect(url_for("my_home") + "#section_5")

if __name__ == "__main__":
    app.run(debug=True)
