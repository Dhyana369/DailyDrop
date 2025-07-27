import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from app import get_word_of_the_day

# CONFIG
import os

MY_EMAIL = os.environ["MY_EMAIL"]
APP_PASSWORD = os.environ["APP_PASSWORD"]
MY_NAME = "DailyDrop Bot"
SUBSCRIBERS_FILE = "subscribers.txt"
SITE_BASEURL = "https://Dhyana.pythonanywhere.com"

def send_emails():
    if not os.path.exists(SUBSCRIBERS_FILE):
        print("No subscribers yet.")
        return
    with open(SUBSCRIBERS_FILE) as f:
        subscribers = [line.strip() for line in f if line.strip()]
    if not subscribers:
        print("No subscribers in list.")
        return

    word_data = get_word_of_the_day(0)
    audio_url = SITE_BASEURL + word_data['audio_url']
    frontend_url = SITE_BASEURL + "/frontend"
    
    body = f"""
<div style="font-family: Arial, Helvetica, sans-serif; color: #000;">
  <h2 style="color:#000;">{word_data['word'].title()}</h2>
  <b style="color:#000;">Part of Speech:</b> <span style="color:#000;">{word_data['part_of_speech'] or '—'}</span><br>
  <b style="color:#000;">Definition:</b> <span style="color:#000;">{word_data['definition'] or '—'}</span><br>
  <b style="color:#000;">Example:</b> <span style="color:#000;">{word_data['example'] or '—'}</span><br>
  <b style="color:#000;">Synonyms:</b> <span style="color:#000;">{', '.join(word_data['synonyms']) or '—'}</span><br>
  <b style="color:#000;">Antonyms:</b> <span style="color:#000;">{', '.join(word_data['antonyms']) or '—'}</span><br>
  <b style="color:#000;">Listen:</b>
  <a href="{audio_url}" target="_blank" style="color:blue; text-decoration: underline;">Click here to hear pronunciation (opens in browser)</a>
  <br><br>
  See full word &amp; play audio on site:
  <a href="{SITE_BASEURL}/frontend" style="color:blue; text-decoration: underline;">{SITE_BASEURL}/frontend</a>
  <br><br>
  — DailyDrop Team
</div>

"""

    subject = f"DailyDrop: {word_data['word'].title()} ({word_data['part_of_speech']})"

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(MY_EMAIL, APP_PASSWORD)
    for email in subscribers:
        msg = MIMEMultipart()
        msg['From'] = formataddr((MY_NAME, MY_EMAIL))
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        try:
            server.sendmail(MY_EMAIL, email, msg.as_string())
            print(f"Sent to {email}")
        except Exception as e:
            print(f"Failed for {email}: {e}")
    server.quit()

if __name__ == '__main__':
    send_emails()
