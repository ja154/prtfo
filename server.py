import os, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed")

# Database Configuration
# Local: postgresql://username:password@localhost:5432/portfolio_db
# Vercel: Use the POSTGRES_URL environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://localhost/portfolio_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Mail Configuration
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() == "true",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "false").lower() == "true",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME")),
)

mail = Mail(app)
RECIPIENT = os.getenv("MAIL_RECIPIENT", "jmwanguwe3@gmail.com")

# Database Model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp_utc = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

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

    try:
        # Store in PostgreSQL
        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        
        # Send Email
        msg = Message(
            subject   = f"Portfolio Contact | {name}",
            sender    = app.config.get("MAIL_DEFAULT_SENDER"),
            recipients = [RECIPIENT],
            reply_to  = email,
            body      = f"Name: {name}\nEmail: {email}\n\n{message}"
        )
        mail.send(msg)
        flash("Thanks! Your message has been sent and saved ✔", "success")
    except Exception as exc:
        print("Error processing message:", exc)
        db.session.rollback()
        flash("There was an error sending your message. Please try again later.", "danger")

    return redirect(url_for("my_home") + "#section_5")

if __name__ == "__main__":
    app.run(debug=True)
