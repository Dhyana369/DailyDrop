import requests
import json
import os
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Load the word of the day
def get_today_word():
    with open("words.json", "r", encoding="utf-8") as f:
        words = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    if today in words:
        return words[today]
    else:
        return None

# Format the message content
def format_message(word_data):
    return f""" *Word of the Day* 

*{word_data['word']}* ({word_data['part_of_speech']})
Meaning: _{word_data['meaning']}_
Pronunciation: /{word_data['pronunciation']}/

Example:
_{word_data['example']}_

Synonyms: {', '.join(word_data['synonyms'])}
Antonyms: {', '.join(word_data['antonyms'])}
"""

# Send the message to Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response.status_code == 200

# Main handler
if __name__ == "__main__":
    word = get_today_word()
    if word:
        message = format_message(word)
        success = send_telegram_message(message)
        if success:
            print("✅ Word sent successfully!")
        else:
            print("❌ Failed to send the word!")
    else:
        print("❌ No word found for today in words.json")
