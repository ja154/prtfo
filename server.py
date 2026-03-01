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
# Vercel provides STORAGE_URL or POSTGRES_URL.
# We use pg8000 as the driver for better serverless compatibility.
database_url = os.getenv("STORAGE_URL") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Add connection pooling settings for serverless environments
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

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

# Function to safely initialize the database on the first request
@app.before_request
def create_tables():
    if not hasattr(app, '_db_initialized'):
        if app.config['SQLALCHEMY_DATABASE_URI']:
            try:
                db.create_all()
                app._db_initialized = True
            except Exception as e:
                print(f"Lazy database initialization error: {e}")
                # Don't set _db_initialized so we can try again later

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

    # Try to store in database if configured
    db_success = False
    if app.config['SQLALCHEMY_DATABASE_URI']:
        try:
            new_msg = ContactMessage(name=name, email=email, message=message)
            db.session.add(new_msg)
            db.session.commit()
            db_success = True
        except Exception as exc:
            print("Database storage error:", exc)
            db.session.rollback()

    # Always try to send email regardless of DB status
    try:
        msg = Message(
            subject   = f"Portfolio Contact | {name}",
            sender    = app.config.get("MAIL_DEFAULT_SENDER"),
            recipients = [RECIPIENT],
            reply_to  = email,
            body      = f"Name: {name}\nEmail: {email}\n\n{message}"
        )
        mail.send(msg)
        
        if db_success:
            flash("Thanks! Your message has been sent and saved ✔", "success")
        else:
            flash("Thanks! Your message has been sent (local storage failed) ✔", "warning")
            
    except Exception as exc:
        print("Email sending error:", exc)
        if db_success:
            flash("Message saved, but email failed to send. I'll check it later!", "warning")
        else:
            flash("There was an error sending your message. Please try again later.", "danger")

    return redirect(url_for("my_home") + "#section_5")

if __name__ == "__main__":
    app.run(debug=True)
