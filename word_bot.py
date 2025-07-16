import json
import requests
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Load word list
with open("words.json", "r") as f:
    words = json.load(f)

# Pick today's word based on date rotation
start_date = datetime(2025, 1, 1).date()
today = datetime.now().date()
index = (today - start_date).days % len(words)
word = words[index]

# Extract fields with fallback
w = word.get("word", "N/A")
pos = word.get("part_of_speech", "Not Available")
mean = word.get("meaning", "Not Available")
example = word.get("example", "Not Available")
synonyms = ", ".join(word.get("synonyms", ["Not Available"]))
antonyms = ", ".join(word.get("antonyms", ["Not Available"]))
pronunciation = word.get("pronunciation", "Not Available")
audio_url = word.get("audio_url", "")

# Format the message
message = f"""
📘 *Word of the Day*

*Word:* {w}
🔈 *Pronunciation:* {pronunciation}
*Part of Speech:* {pos}

*Meaning:* {mean}

💡 *Example:* {example}

synonyms_line = f"*Synonyms:* {word_data['synonyms']}" if word_data['synonyms'] != 'None found.' else ""
antonyms_line = f"*Antonyms:* {word_data['antonyms']}" if word_data['antonyms'] != 'None found.' else ""
"""

# Send message to Telegram
def send_to_telegram(chat_id, message, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    print("✅ Message sent:", res.status_code)

send_to_telegram(CHAT_ID, message, BOT_TOKEN)
