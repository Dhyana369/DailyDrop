import requests
from datetime import date, timedelta
from flask import Flask, jsonify, send_from_directory, request
from gtts import gTTS
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, DailyDrop!"

@app.route('/frontend')
def serve_frontend():
    return send_from_directory('.', 'index.html')

def extract_all_synonyms_antonyms(data):
    synonyms = set()
    antonyms = set()
    for meaning in data.get("meanings", []):
        # Definition-level
        for definition in meaning.get("definitions", []):
            synonyms.update(definition.get("synonyms", []))
            antonyms.update(definition.get("antonyms", []))
        synonyms.update(meaning.get("synonyms", []))
        antonyms.update(meaning.get("antonyms", []))
    return list(synonyms)[:5], list(antonyms)[:5]

def extract_first_example(data):
    for meaning in data.get("meanings", []):
        for definition in meaning.get("definitions", []):
            if 'example' in definition and definition['example']:
                return definition['example']
    return ""

def get_word_of_the_day(days_ago=0):
    with open("words.txt", "r") as f:
        word_list = [w.strip() for w in f if w.strip()]
    total_words = len(word_list)
    start_date = date(2025, 1, 1)
    target_date = date.today() - timedelta(days=days_ago)
    days_since_start = (target_date - start_date).days
    word_index = days_since_start % total_words
    word = word_list[word_index]

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url, timeout=6)
        if response.status_code != 200:
            raise Exception("DictionaryAPI.dev error")
        data = response.json()[0]
        synonyms, antonyms = extract_all_synonyms_antonyms(data)
        example = extract_first_example(data)
        word_data = {
            "word": data.get("word", word),
            "part_of_speech": data["meanings"][0]["partOfSpeech"] if data.get("meanings") else "",
            "definition": data["meanings"][0]["definitions"][0]["definition"] if data.get("meanings") else "",
            "example": example,
            "synonyms": synonyms,
            "antonyms": antonyms
        }
    except Exception as e:
        print("DictionaryAPI fetch failed:", e)
        word_data = {  # fallback on error
            "word": word, "part_of_speech": "", "definition": "",
            "example": "", "synonyms": [], "antonyms": []
        }

    # Audio generation
    audio_folder = "static/audio"
    os.makedirs(audio_folder, exist_ok=True)
    audio_path = os.path.join(audio_folder, f"{word}.mp3")
    if not os.path.exists(audio_path):
        try:
            tts = gTTS(word, lang="en")
            tts.save(audio_path)
            print(f"Audio saved: {audio_path}")
        except Exception as e:
            print("Failed to generate audio:", e)
    else:
        print("Audio already exists:", audio_path)
    word_data["audio_url"] = f"/static/audio/{word}.mp3"
    return word_data

@app.route('/word-of-the-day')
def word_of_the_day_route():
    days_ago = int(request.args.get('days_ago', 0))
    word_data = get_word_of_the_day(days_ago)
    return jsonify(word_data)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email or '@' not in email:
        return {"error": "Enter a valid email address"}, 400
    email = email.strip().lower()
    if os.path.exists('subscribers.txt'):
        with open('subscribers.txt', 'r') as subfile:
            emails = set(x.strip() for x in subfile)
        if email in emails:
            return {"message": "Already subscribed!"}, 200
    with open('subscribers.txt', 'a') as subfile:
        subfile.write(email + "\n")
    return {"message": "Subscribed successfully! 🎉"}, 200

if __name__ == '__main__':
    app.run(debug=True)
