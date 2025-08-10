from flask import Flask, jsonify, render_template, request, redirect, url_for
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
print("DEBUG: Flask is using DB:", DB_PATH)

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Table for words
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE,
            meaning TEXT,
            example TEXT,
            synonyms TEXT,
            antonyms TEXT,
            audio_url TEXT,
            created_at DATE DEFAULT CURRENT_DATE
        )
    ''')
    # Table for subscribers
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/today', methods=['GET'])
def get_today():
    today = date.today().isoformat()
    conn = get_db_connection()
    word = conn.execute('SELECT * FROM words WHERE created_at = ? LIMIT 1', (today,)).fetchone()
    conn.close()
    if word:
        return jsonify(dict(word))
    return jsonify({"message": "No words found for today"})

@app.route('/week', methods=['GET'])
def get_week():
    conn = get_db_connection()
    words = conn.execute('SELECT * FROM words ORDER BY created_at DESC LIMIT 7').fetchall()
    conn.close()
    return jsonify([dict(w) for w in words])

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        conn.close()
        print(f"New subscriber added: {email}")

        # --- Send confirmation email ---
        subject = "Welcome to DailyDrop!"
        body = f"""Hi,
\nYou have successfully subscribed to DailyDrop.
You will start receiving daily words at 8:00 AM IST.

\nIf this wasn't you, you can unsubscribe here:
https://dhyana.pythonanywhere.com/unsubscribe?email={email}
"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER  # Replace with your Gmail
        msg['To'] = email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)  # Replace with app password
            server.sendmail(GMAIL_USER, email, msg.as_string())
        return jsonify({"status": "success", "message": "Thanks for subscribing!"})

    except sqlite3.IntegrityError:
            # Email already exists
        print(f"Duplicate subscription attempt: {email}")
        return jsonify({"status": "error", "message": "You are already subscribed."})
    except Exception as e:
        print(f"Subscription error: {e}")
        return jsonify({"status": "error", "message": "Subscription failed. Please try again."}), 500

@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email')
    if email:
        conn = get_db_connection()
        conn.execute('DELETE FROM subscribers WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        return f"""
        <html>
          <body style='font-family: Arial, sans-serif; text-align: center; padding: 50px;'>
            <h2>{email} has been unsubscribed from DailyDrop.</h2>
            <a href='/' style='color: #5B2C6F; text-decoration: none;'>Return to website</a>
          </body>
        </html>
        """
    return "<h2>No email specified.</h2>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
