import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Load word list
with open("words.json", "r") as f:
    words = json.load(f)

# Pick today's word
start_date = datetime(2025, 1, 1).date()
today = datetime.now().date()
index = (today - start_date).days % len(words)
word = words[index]

# Extract fields with fallback
w = word.get("word", "N/A")
pos = word.get("part_of_speech", "—")
mean = word.get("meaning", "—")
example = word.get("example", "—")
pronunciation = word.get("pronunciation", "—")

# Format Synonyms & Antonyms
synonyms_list = word.get("synonyms", [])
synonyms = ", ".join(synonyms_list) if synonyms_list else "—"

antonyms_list = word.get("antonyms", [])
antonyms = ", ".join(antonyms_list) if antonyms_list else "—"

# Format the message
message = f"""
📘 *Word of the Day*

*Word:* {w}
🔈 *Pronunciation:* {pronunciation}
*Part of Speech:* {pos}

*Meaning:* {mean}

💡 *Example:* {example}

*Synonyms:* {synonyms}
*Antonyms:* {antonyms}
"""

# Send to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}
res = requests.post(url, json=payload)
print("✅ Message sent:", res.status_code)
