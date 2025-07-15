import requests
import random
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Pick a random word from file
def get_random_word():
    with open("word_list.txt", "r") as f:
        words = f.read().splitlines()
    return random.choice(words)

# Fetch data from dictionary API
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    data = response.json()

    try:
        meaning_data = data[0]['meanings'][0]
        definitions = meaning_data['definitions'][0]
        phonetics = data[0]['phonetics'][0]

        word_info = {
            "word": word,
            "part_of_speech": meaning_data['partOfSpeech'],
            "meaning": definitions['definition'],
            "example": definitions.get('example', 'No example available.'),
            "synonyms": ', '.join(definitions.get('synonyms', [])[:3]) or 'None found.',
            "antonyms": ', '.join(definitions.get('antonyms', [])[:3]) or 'None found.',
            "pronunciation": phonetics.get('text', '—'),
            "audio_url": phonetics.get('audio', '')
        }

        return word_info
    except Exception as e:
        print(f"❌ Error fetching word data: {e}")
        return None

# Format the message
def format_message(word_data):
    return f"""
📘 *Word of the Day*

*Word:* {word_data['word']}
🔈 *Pronunciation:* {word_data['pronunciation']}
*Part of Speech:* {word_data['part_of_speech']}

*Meaning:* {word_data['meaning']}

💡 *Example:* {word_data['example']}

*Synonyms:* {word_data['synonyms']}
*Antonyms:* {word_data['antonyms']}
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

# --- MAIN LOGIC ---

word = get_random_word()
word_data = get_word_data(word)

if word_data:
    message = format_message(word_data)
    send_to_telegram(CHAT_ID, message, BOT_TOKEN)
else:
    print("❌ Could not send message. Word data not available.")
