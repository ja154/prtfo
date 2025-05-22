import os, json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Corrected: os.getenv() should look for an environment variable named "SECRET_KEY"
# The actual secret key value must be set on Render's environment variables.
app.secret_key = os.getenv("SECRET_KEY")

# ------------ Flask‑Mail configuration -------------
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "false").lower() == "true",
    # Corrected: os.getenv() should look for an environment variable named "MAIL_USERNAME"
    # The actual email address must be set on Render's environment variables.
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    # Corrected: os.getenv() should look for an environment variable named "MAIL_PASSWORD"
    # The actual App Password must be set on Render's environment variables.
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
)
print("MAIL_DEFAULT_SENDER =", app.config.get("MAIL_DEFAULT_SENDER"))
print("MAIL_USERNAME       =", app.config.get("MAIL_USERNAME"))

mail = Mail(app)
# It's good practice to also make RECIPIENT an environment variable if it changes
# RECIPIENT = os.getenv("MAIL_RECIPIENT", "jmwanguwe3@gmail.com")
RECIPIENT = "jmwanguwe3@gmail.com" # Keeping as hardcoded for now as per your original code
LOG_PATH = Path("messages.log")

# ---------- helper to persist every message ----------
def write_to_file(data: dict):
    """Append one JSON line to messages.log with timestamp."""
    data["timestamp_utc"] = datetime.utcnow().isoformat(timespec="seconds")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
# -----------------------------------------------------

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

    # 1. persist locally
    write_to_file({"name": name, "email": email, "message": message})

    # 2. send the e‑mail
    msg = Message(
        subject   = f"Portfolio Contact | {name}",
        sender    = "jmwanguwe3@gmail.com",       # hard‑coded sender
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
