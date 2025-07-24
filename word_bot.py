import requests
import random
import os
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

# Telegram Bot Token and Chat ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize the bot
bot = Bot(token=TELEGRAM_TOKEN)

# Function to fetch word data from the API
def get_word_data():
    try:
        response = requests.get("https://api.api-ninjas.com/v1/dictionary?word=random", headers={
            'X-Api-Key': os.getenv("NINJA_API_KEY")
        })

        if response.status_code == 200:
            data = response.json()
            word = data['word']
        else:
            word = random.choice(["serene", "eloquent", "arduous", "lucid", "candid"])

        # Now get extended info
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        r = requests.get(url)

        if r.status_code != 200:
            raise Exception("Word data fetch failed.")

        entry = r.json()[0]
        meaning_data = list(entry['meanings'][0]['definitions'])[0]

        word_data = {
            "word": word,
            "pronunciation": entry.get("phonetic", "/unknown/"),
            "part_of_speech": entry['meanings'][0]['partOfSpeech'],
            "meaning": meaning_data.get("definition", "No definition available."),
            "example": meaning_data.get("example", "No example available."),
            "synonyms": entry['meanings'][0].get("synonyms", []),
            "antonyms": entry['meanings'][0].get("antonyms", [])
        }

        return word_data

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to format and send the message
def send_word_message():
    word_data = get_word_data()
    if not word_data:
        print("Failed to fetch word data.")
        return

    message = (
        f"📘 *Word of the Day*\n\n"
        f"*Word:* {word_data['word']}\n"
        f"🔈 *Pronunciation:* /{word_data['pronunciation']}/\n"
        f"*Part of Speech:* {word_data['part_of_speech']}\n"
        f"*Meaning:* {word_data['meaning']}\n"
        f"💡 *Example:* {word_data['example']}\n"
        f"*Synonyms:* {', '.join(word_data['synonyms'][:5]) or 'None found'}\n"
        f"*Antonyms:* {', '.join(word_data['antonyms'][:5]) or 'None found'}"
    )

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
    print("✅ Word of the Day sent to Telegram!")

# Run the bot
if __name__ == "__main__":
    send_word_message()
