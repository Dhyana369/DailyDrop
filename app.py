from flask import Flask, jsonify, render_template, request, redirect
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            word           TEXT UNIQUE,
            part_of_speech TEXT DEFAULT '',
            meaning        TEXT,
            example        TEXT,
            synonyms       TEXT,
            antonyms       TEXT,
            phonetic       TEXT DEFAULT '',
            audio_url      TEXT,
            created_at     DATE DEFAULT CURRENT_DATE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    """)
    # Add new columns if upgrading from old schema
    for col, definition in [("part_of_speech", "TEXT DEFAULT ''"), ("phonetic", "TEXT DEFAULT ''")]:
        try:
            conn.execute(f"ALTER TABLE words ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/today")
def get_today():
    today = date.today().isoformat()
    conn = get_db_connection()
    word = conn.execute("SELECT * FROM words WHERE created_at = ? LIMIT 1", (today,)).fetchone()
    conn.close()
    if word:
        return jsonify(dict(word))
    return jsonify({"message": "No word found for today"})


@app.route("/week")
def get_week():
    conn = get_db_connection()
    # Last 7 days excluding today
    today = date.today().isoformat()
    words = conn.execute(
        "SELECT * FROM words WHERE created_at < ? ORDER BY created_at DESC LIMIT 7",
        (today,)
    ).fetchall()
    conn.close()
    return jsonify([dict(w) for w in words])


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()
    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO subscribers (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()

        # Confirmation email
        body = f"""Hi,

You've successfully subscribed to DailyDrop! 🎉
You'll receive a new word every morning at 8:00 AM IST.

Visit us: https://dhyana.pythonanywhere.com/

If this wasn't you, unsubscribe here:
https://dhyana.pythonanywhere.com/unsubscribe?email={email}
"""
        msg = MIMEText(body)
        msg["Subject"] = "Welcome to DailyDrop!"
        msg["From"] = GMAIL_USER
        msg["To"] = email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, email, msg.as_string())

        return jsonify({"status": "success", "message": "You're subscribed! Check your inbox."})

    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "You're already subscribed."})
    except Exception as e:
        print(f"Subscription error: {e}")
        return jsonify({"status": "error", "message": "Something went wrong. Try again."}), 500


@app.route("/unsubscribe")
def unsubscribe():
    email = request.args.get("email", "").strip()
    if email:
        conn = get_db_connection()
        conn.execute("DELETE FROM subscribers WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return f"""
        <html>
          <head><title>Unsubscribed – DailyDrop</title></head>
          <body style="font-family:Georgia,serif;text-align:center;padding:60px;background:#F7F4EF;color:#1A1A1A;">
            <h2>You've been unsubscribed.</h2>
            <p style="color:#888;">{email} has been removed from DailyDrop.</p>
            <a href="/" style="color:#D4A017;font-weight:bold;text-decoration:none;">← Back to DailyDrop</a>
          </body>
        </html>
        """
    return "<h2>No email specified.</h2>"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
