import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load .env
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

def get_subscribers():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT email FROM subscribers').fetchall()
    conn.close()
    return [r[0] for r in rows]

def send_email(to_email, subject, html):
    msg = MIMEText(html, 'html')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

def send_email_to_all(word):
    if not word:
        print("No word data passed!")
        return

    subscribers = get_subscribers()
    print(f"Sending email to {len(subscribers)} subscribers...")

    for email in subscribers:
        html = f"""
        <html>
          <body style="font-family: Garamond, sans-serif; background-color: #f9f9f9; padding: 20px; font-size: 18px; line-height: 1.6;">
            <div style="max-width: 700px; margin: auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #000;">

              <h1 style="text-align: center; color: #000; margin-bottom: 10px; font-size: 32px;">DailyDrop</h1>

              <hr style="border: none; border-top: 2px solid #EAEAEA; margin: 20px 0;">

              <h2 style="color: #000; font-size: 24px;">Word of the Day:
                <span style="font-weight: bold;">{word['word']}</span>
              </h2>

              <p><strong>Meaning:</strong> {word['meaning']}</p>
              <p><strong>Example:</strong> {word['example']}</p>
              <p><strong>Synonyms:</strong> {word['synonyms']}</p>
              <p><strong>Antonyms:</strong> {word['antonyms']}</p>

              <div style="text-align:center; margin-top: 30px;">
                <a href="https://dhyana.pythonanywhere.com/"
                   style="background-color:#5B2C6F; color:white; text-decoration:none; padding: 14px 24px; border-radius: 8px; font-size: 18px;">
                  Visit Website
                </a>
              </div>

              <p style="margin-top: 30px; font-size: 12px; color: #666; text-align: center;">
                You're receiving this email because you subscribed to DailyDrop.<br>
              </p>
              <p style="font-size: 12px; color: #666; text-align: center; margin-top:20px;">
                <a href="https://dhyana.pythonanywhere.com/unsubscribe?email={email}" style="color:#5B2C6F;">Unsubscribe</a>
              </p>
            </div>
          </body>
        </html>
        """
        send_email(email, f"DailyDrop: {word['word']}", html)

    print("Emails sent successfully!")

# Only for testing this script directly (not used in deployment now)
if __name__ == "__main__":
    print("This script should be called from daily_job.py with word data.")
