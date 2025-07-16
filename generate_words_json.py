import time
import requests
import json

def fetch_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()[0]

        phonetics = next((p for p in data.get("phonetics", []) if p.get("text")), {})
        audio = next((p for p in data.get("phonetics", []) if p.get("audio")), {})

        meaning = data.get("meanings", [])[0]
        definition = meaning.get("definitions", [])[0]

        return {
            "word": word,
            "part_of_speech": meaning.get("partOfSpeech", "Not Available"),
            "meaning": definition.get("definition", "Not Available"),
            "example": definition.get("example", "No example available."),
            "synonyms": definition.get("synonyms", [])[:5] or ["None found."],
            "antonyms": definition.get("antonyms", [])[:5] or ["None found."],
            "pronunciation": phonetics.get("text", "—"),
            "audio_url": audio.get("audio", "")
        }
    except Exception as e:
        print(f"❌ Error fetching: {word} | {e}")
        return {
            "word": word,
            "part_of_speech": "Not Available",
            "meaning": "Not Available",
            "example": "No example available.",
            "synonyms": ["None found."],
            "antonyms": ["None found."],
            "pronunciation": "—",
            "audio_url": ""
        }

# Read words from file
with open("word_list.txt", "r") as file:
    word_list = file.read().splitlines()

word_data = []
for word in word_list:
    print(f"🔍 Fetching: {word}...")
    word_data.append(fetch_word_data(word))
    time.sleep(1.5)  # ⏱️ Delay between requests

# Save to JSON
with open("words.json", "w") as f:
    json.dump(word_data, f, indent=2)

print("✅ words.json created with enriched data.")
