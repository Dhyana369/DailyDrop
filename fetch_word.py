import sqlite3
import requests
import random
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

# List of random words
WORD_LIST = [
    "serendipity", "ephemeral", "labyrinth", "eloquent", "resilient", "tranquil", "enigmatic", "benevolent", "ubiquitous", "aesthetic",
    "aberration", "acquiesce", "adamant", "adulation", "affable", "alacrity", "ambivalent", "amiable", "amorphous", "anecdote",
    "animosity", "anomaly", "antipathy", "apex", "apathy", "arbitrary", "ardent", "artifice", "astute", "austere",
    "avarice", "bellicose", "belligerent", "benevolence", "blatant", "brevity", "cacophony", "candor", "capitulate", "cathartic",
    "clandestine", "cogent", "coherent", "complacent", "conundrum", "copious", "cryptic", "culpable", "cursory", "dauntless",
    "debacle", "debilitate", "decorum", "deleterious", "demure", "deride", "despondent", "destitute", "diligent", "discern",
    "discord", "disdain", "disingenuous", "disparage", "disseminate", "divergent", "docile", "dubious", "eclectic", "egregious",
    "elated", "elicit", "elucidate", "emulate", "enervate", "enigma", "enthrall", "enumerate", "ephemeralness", "equanimity",
    "equivocate", "eradicate", "erratic", "erudite", "esoteric", "ethereal", "exacerbate", "exculpate", "exemplary", "exonerate",
    "expedite", "fallacy", "fastidious", "fatuous", "fervent", "flagrant", "flamboyant", "fortuitous", "fractious", "frugal",
    "futile", "garrulous", "gratuitous", "gregarious", "hackneyed", "haughty", "hedonist", "heresy", "holistic", "hubris",
    "hyperbole", "idiosyncrasy", "ignominious", "illustrious", "immanent", "impeccable", "impervious", "implacable", "implicit", "impromptu",
    "inadvertent", "inane", "abhor", "acumen", "adept", "adjacent", "admonish", "affluent", "ailment", "allude", "aloof", "altercation",
    "amiable", "ample", "angst", "arduous", "articulate", "ascend", "aspire", "astound", "attest", "avid",
    "banter", "befuddle", "behoove", "belittle", "benign", "blunder", "boisterous", "bolster", "brandish", "brusque",
    "candid", "canny", "carp", "chide", "coax", "commend", "conceive", "condone", "confer", "conjure",
    "copious", "cordial", "counterfeit", "covet", "coy", "crass", "curtail", "daunt", "decree", "deem",
    "defiant", "delve", "demeanor", "denote", "deter", "detract", "devise", "digress", "diligent", "disclose",
    "dispel", "dissuade", "divulge", "docile", "dote", "dubious", "earnest", "eclectic", "elated", "elicit",
    "elude", "embark", "emulate", "enact", "endear", "endure", "enlist", "ensue", "entail", "entice",
    "envisage", "equate", "eradicate", "erratic", "espouse", "evade", "evoke", "exalt", "excel", "exert",
    "exile", "expedite", "exploit", "extol", "falter", "feign", "fend", "feral", "fester", "flaunt",
    "flinch", "flounder", "forgo", "fortify", "fray", "fret", "frivolous", "gauge", "glean", "gloat",
    "grapple", "grieve", "guise", "haggle", "hamper", "heed", "hoard", "hurl", "immerse", "impede",
    "implore", "incite", "indulge", "inflict", "inhabit", "instill", "invoke", "jostle", "lament", "latch",
    "linger", "loathe", "lurk", "mimic", "mull", "muster", "nurture", "omit", "outwit", "oversee"
]


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_random_word():
    return random.choice(WORD_LIST)

def fetch_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()[0]
        meaning = data["meanings"][0]["definitions"][0].get("definition", "")
        example = data["meanings"][0]["definitions"][0].get("example", "")
        synonyms = ", ".join(data["meanings"][0].get("synonyms", []))
        antonyms = ", ".join(data["meanings"][0].get("antonyms", []))

        # Audio URL
        audio = ""
        phonetics = data.get("phonetics", [])
        for ph in phonetics:
            if "audio" in ph and ph["audio"]:
                audio = ph["audio"]
                break

        return {
            "word": word,
            "meaning": meaning,
            "example": example,
            "synonyms": synonyms,
            "antonyms": antonyms,
            "audio_url": audio
        }
    except Exception as e:
        print("Error fetching word:", e)
        return None

def word_exists(word):
    conn = get_db_connection()
    res = conn.execute("SELECT 1 FROM words WHERE word = ?", (word,)).fetchone()
    conn.close()
    return res is not None

def insert_word(data):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO words (word, meaning, example, synonyms, antonyms, audio_url, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data["word"], data["meaning"], data["example"],
            data["synonyms"], data["antonyms"], data["audio_url"],
            datetime.date.today().isoformat()
        )
    )
    conn.commit()
    conn.close()
    print(f"Inserted new word: {data['word']}")

def fetch_and_save_word():
    today = datetime.date.today().isoformat()

    # Check if a word already exists for today
    conn = get_db_connection()
    word = conn.execute("SELECT * FROM words WHERE created_at = ?", (today,)).fetchone()
    conn.close()

    if word:
        print(f"Word for today ({today}) already exists: {word['word']}")
        return dict(word)

    # No word for today, pick a new random word
    while True:
        word_candidate = fetch_random_word()

        # Skip if word already exists in DB for previous days
        if word_exists(word_candidate):
            print(f"{word_candidate} already exists from previous day, picking another...")
            continue

        # Fetch word data from API
        data = fetch_word_data(word_candidate)
        if not data:
            print("No data fetched for the word:", word_candidate)
            return None

        # Insert new word with today's date
        insert_word(data)
        print(f"Inserted new word for today: {data['word']}")
        return data

def get_latest_word():
    conn = get_db_connection()
    word = conn.execute('SELECT * FROM words ORDER BY created_at DESC LIMIT 1').fetchone()
    conn.close()
    if word:
        return dict(word)
    return None


if __name__ == "__main__":
    fetch_and_save_word()
