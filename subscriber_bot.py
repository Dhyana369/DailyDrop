import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
SUBSCRIBERS_FILE = "subscribers.txt"

def get_updates(offset=None):
    params = {"timeout": 1, "offset": offset}
    response = requests.get(URL + "getUpdates", params=params)
    return response.json().get("result", [])

def save_subscriber(chat_id):
    if not os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "w") as f:
            pass

    with open(SUBSCRIBERS_FILE, "r") as f:
        existing = f.read().splitlines()

    if str(chat_id) not in existing:
        with open(SUBSCRIBERS_FILE, "a") as f:
            f.write(str(chat_id) + "\n")
        print(f"✅ New subscriber added: {chat_id}")
        send_message(chat_id, "Thanks for subscribing to the Daily Word Bot!")
    else:
        print(f"ℹ️ Already subscribed: {chat_id}")

def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    requests.post(URL + "sendMessage", json=payload)

def run_bot():
    print("🤖 Listening for /start messages...")
    offset = None

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1

            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id")

            if text == "/start":
                save_subscriber(chat_id)

        time.sleep(2)

if __name__ == "__main__":
    run_bot()
