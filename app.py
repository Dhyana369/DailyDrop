from flask import Flask, jsonify, render_template, request, redirect # web framework
import sqlite3 # database, stores words and subscribers
import os # file path and environment varables
import smtplib # sending emails
from email.mime.text import MIMEText 
from dotenv import load_dotenv # loads .env file
from datetime import date, timedelta # works with dates

# Environment setup
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Database path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")


# create flask app
app = Flask(__name__) # initializing web app

# Database connection function
def get_db_connection(): 
    conn = sqlite3.connect(DB_PATH) # opens db connection
    conn.row_factory = sqlite3.Row # allows accessing columns like dictionary
    return conn

# initializing database
def init_db():
    conn = get_db_connection() # creates tables
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
    # Add new columns if upgrading from old schema prevents breaking old database
    for col, definition in [("part_of_speech", "TEXT DEFAULT ''"), ("phonetic", "TEXT DEFAULT ''")]:
        try:
            conn.execute(f"ALTER TABLE words ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # Column already exists
    conn.commit()
    conn.close()

# Home page
@app.route("/")
def home():
    return render_template("index.html") # loads frontend page

# Get today's word
@app.route("/today")
def get_today():
    today = date.today().isoformat() # get today's date
    conn = get_db_connection()
    word = conn.execute("SELECT * FROM words WHERE created_at = ? LIMIT 1", (today,)).fetchone() # fetchs today's word
    conn.close()
    if word:
        return jsonify(dict(word)) # converts db row to json, frontend or apps expect data in json format
    return jsonify({"message": "No word found for today"})

# get last week words
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

# Subscribe feature 
@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip() # get email
    if not email: # validate
        return jsonify({"status": "error", "message": "Email is required."}), 400
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO subscribers (email) VALUES (?)", (email,)) # store in db
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
        # sending confirmation email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  # uses gmail smtp server
            server.login(GMAIL_USER, GMAIL_PASSWORD) # authenticate
            server.sendmail(GMAIL_USER, email, msg.as_string()) # sends email

        return jsonify({"status": "success", "message": "You're subscribed! Check your inbox."})

    # error handling
    except sqlite3.IntegrityError: # prevents duplicate subscriptions
        return jsonify({"status": "error", "message": "You're already subscribed."})
    except Exception as e: # prevents crash
        print(f"Subscription error: {e}")
        return jsonify({"status": "error", "message": "Something went wrong. Try again."}), 500

# unsubscribe feature
@app.route("/unsubscribe")
def unsubscribe():
    email = request.args.get("email", "").strip() # gets email
    if email:
        conn = get_db_connection()
        conn.execute("DELETE FROM subscribers WHERE email = ?", (email,)) # deletes from db
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
