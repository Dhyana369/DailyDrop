import sqlite3
import requests
import random
import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

MW_DICT_KEY      = os.getenv("MW_DICT_KEY")
MW_THESAURUS_KEY = os.getenv("MW_THESAURUS_KEY")

# Curated word list — common enough for MW to have full data
WORD_LIST = [
    "ephemeral", "acquiesce", "adamant", "alacrity", "ambivalent", "amiable",
    "anomaly", "antipathy", "apathy", "ardent", "avarice", "bellicose",
    "benevolence", "brevity", "cacophony", "candor", "cathartic", "clandestine",
    "cogent", "complacent", "conundrum", "copious", "cryptic", "culpable",
    "dauntless", "debacle", "deleterious", "demure", "disdain", "disparage",
    "dubious", "egregious", "elated", "elucidate", "enigma", "equanimity",
    "erudite", "esoteric", "ethereal", "exacerbate", "exemplary", "fallacy",
    "fervent", "flagrant", "frugal", "futile", "garrulous", "gregarious",
    "haughty", "hedonist", "holistic", "impeccable", "implicit", "inadvertent",
    "abhor", "acumen", "adept", "admonish", "affluent", "aloof",
    "arduous", "articulate", "aspire", "avid", "benign", "bolster",
    "candid", "coax", "commend", "condone", "cordial", "covet",
    "curtail", "daunt", "delve", "demeanor", "deter", "digress",
    "divulge", "earnest", "elude", "embark", "endure", "entice",
    "evoke", "exalt", "falter", "feign", "flinch", "flounder",
    "fortify", "frivolous", "glean", "gloat", "grapple", "hamper",
    "heed", "immerse", "impede", "implore", "incite", "indulge",
    "instill", "invoke", "lament", "linger", "loathe", "mimic",
    "muster", "nurture", "outwit", "oversee", "persevere", "placid",
    "pragmatic", "pristine", "profound", "resilient", "sagacious", "serene",
    "tenacious", "verbose", "vigilant", "vivacious", "zealous", "aberration",
    "abstain", "acrimony", "adhere", "adversity", "affinity", "aggravate",
    "agile", "alleviate", "altruism", "ambiguous", "ameliorate", "amplify",
    "anarchy", "antagonize", "appease", "apprehend", "ardor", "aversion",
    "baffle", "benevolent", "boisterous", "brazen", "callous", "censure",
    "coerce", "compassion", "compel", "comply", "comprehend", "concede",
    "condemn", "contempt", "contentious", "contradict", "conviction", "defiant",
    "deplore", "deprive", "derive", "despise", "diligent", "diminish",
    "discern", "dismiss", "dispute", "disrupt", "diverge", "dominant",
    "elaborate", "elevate", "eloquent", "empower", "endorse", "enhance",
    "enrich", "escalate", "esteem", "exploit", "expose", "facilitate",
    "fierce", "flourish", "foster", "generate", "grasp", "gratitude",
    "hinder", "humble", "illuminate", "impartial", "impose", "inspire",
    "integrity", "justify", "lenient", "liberate", "manipulate", "mediate",
    "minimize", "motivate", "negate", "negotiate", "objective", "obstruct",
    "oppress", "overcome", "passion", "perceive", "persuade", "provoke",
    "pursue", "retaliate", "revere", "scrutinize", "sincere", "skeptical",
    "strive", "suppress", "sustain", "tolerate", "transform", "undermine",
    "unify", "validate", "versatile", "whimsical", "zeal", "tenacity",
    "stoic", "sanguine", "pensive", "melancholy", "languid", "jubilant",
    "inquisitive", "humble", "fervor", "exuberant", "earnest", "diligent",
    "conscientious", "buoyant", "assertive", "astute", "amiable", "ambitious"
]


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_used_words():
    conn = get_db_connection()
    rows = conn.execute("SELECT word FROM words").fetchall()
    conn.close()
    return {r["word"].lower() for r in rows}


def fetch_mw_dictionary(word):
    """Fetch definition, example, part of speech, and pronunciation from MW Collegiate Dictionary."""
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}"
    try:
        resp = requests.get(url, params={"key": MW_DICT_KEY}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()

        # MW returns a list of strings (suggestions) if word not found
        if not data or not isinstance(data[0], dict):
            return None

        entry = data[0]

        # Part of speech
        part_of_speech = entry.get("fl", "")

        # Definition — MW uses 'shortdef' for clean definitions
        shortdefs = entry.get("shortdef", [])
        meaning = shortdefs[0] if shortdefs else ""
        if not meaning:
            return None

        # Example sentence — found in 'def' > 'sseq' > 'dt' > 'vis'
        example = ""
        try:
            for def_block in entry.get("def", []):
                for sseq in def_block.get("sseq", []):
                    for sense in sseq:
                        if isinstance(sense, list) and len(sense) > 1:
                            dt_list = sense[1].get("dt", [])
                            for dt in dt_list:
                                if isinstance(dt, list) and dt[0] == "vis":
                                    for vis in dt[1]:
                                        raw = vis.get("t", "")
                                        # Clean MW markup tags like {it}, {bc}, {sx}
                                        import re
                                        clean = re.sub(r'\{[^}]+\}', '', raw).strip()
                                        if clean:
                                            example = clean
                                            break
                                if example:
                                    break
                        if example:
                            break
                if example:
                    break
        except Exception:
            pass

        # Pronunciation (phonetic text)
        phonetic = ""
        try:
            hwi = entry.get("hwi", {})
            prs = hwi.get("prs", [])
            if prs:
                phonetic = prs[0].get("mw", "")
                # Format as IPA-style with slashes
                if phonetic:
                    phonetic = f"/{phonetic}/"
        except Exception:
            pass

        # Audio URL — MW audio format
        audio_url = ""
        try:
            prs = entry.get("hwi", {}).get("prs", [])
            for pr in prs:
                audio = pr.get("sound", {}).get("audio", "")
                if audio:
                    # Determine subdirectory
                    if audio.startswith("bix"):
                        subdir = "bix"
                    elif audio.startswith("gg"):
                        subdir = "gg"
                    elif audio[0].isdigit() or audio[0] in "_":
                        subdir = "number"
                    else:
                        subdir = audio[0]
                    audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio}.mp3"
                    break
        except Exception:
            pass

        return {
            "word": word,
            "part_of_speech": part_of_speech,
            "meaning": meaning,
            "example": example,
            "phonetic": phonetic,
            "audio_url": audio_url,
        }

    except Exception as e:
        print(f"MW Dictionary error for '{word}':", e)
        return None


def fetch_mw_thesaurus(word):
    """Fetch synonyms and antonyms from MW Collegiate Thesaurus."""
    url = f"https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{word}"
    try:
        resp = requests.get(url, params={"key": MW_THESAURUS_KEY}, timeout=10)
        if resp.status_code != 200:
            return "", ""
        data = resp.json()

        if not data or not isinstance(data[0], dict):
            return "", ""

        synonyms_set = set()
        antonyms_set = set()

        for entry in data:
            for def_block in entry.get("def", []):
                for sseq in def_block.get("sseq", []):
                    for sense in sseq:
                        if not isinstance(sense, list) or len(sense) < 2:
                            continue
                        sense_data = sense[1]

                        # Synonyms — stored under 'syn_list'
                        for group in sense_data.get("syn_list", []):
                            for item in group:
                                if isinstance(item, dict):
                                    w = item.get("wd", "").strip()
                                    if w:
                                        synonyms_set.add(w)

                        # Antonyms — stored under 'ant_list'
                        for group in sense_data.get("ant_list", []):
                            for item in group:
                                if isinstance(item, dict):
                                    w = item.get("wd", "").strip()
                                    if w:
                                        antonyms_set.add(w)

        synonyms = ", ".join(sorted(synonyms_set)[:6])
        antonyms = ", ".join(sorted(antonyms_set)[:6])
        return synonyms, antonyms

    except Exception as e:
        print(f"MW Thesaurus error for '{word}':", e)
        return "", ""


def fetch_word_data(word):
    """Fetch full word data combining MW Dictionary + Thesaurus."""
    dict_data = fetch_mw_dictionary(word)
    if not dict_data or not dict_data.get("meaning"):
        return None

    # Only accept words that have an example sentence
    if not dict_data.get("example"):
        print(f"  ✗ '{word}' — no example sentence.")
        return None

    synonyms, antonyms = fetch_mw_thesaurus(word)
    dict_data["synonyms"] = synonyms
    dict_data["antonyms"] = antonyms

    return dict_data


def word_exists(word):
    conn = get_db_connection()
    res = conn.execute("SELECT 1 FROM words WHERE word = ?", (word,)).fetchone()
    conn.close()
    return res is not None


def insert_word(data):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO words
           (word, part_of_speech, meaning, example, synonyms, antonyms, phonetic, audio_url, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["word"], data["part_of_speech"], data["meaning"], data["example"],
            data["synonyms"], data["antonyms"], data["phonetic"], data["audio_url"],
            datetime.date.today().isoformat()
        )
    )
    conn.commit()
    conn.close()
    print(f"Inserted new word: {data['word']}")


def pick_new_word(used_words):
    available = [w for w in WORD_LIST if w not in used_words]
    random.shuffle(available)

    for word in available:
        print(f"Trying '{word}'...")
        data = fetch_word_data(word)
        if not data:
            time.sleep(0.2)
            continue
        print(f"  ✓ '{word}' — meaning: '{data['meaning'][:50]}...'")
        print(f"         example:  '{data['example'][:60]}...'")
        print(f"         synonyms: '{data['synonyms'] or 'none'}'")
        print(f"         antonyms: '{data['antonyms'] or 'none'}'")
        return data

    print("All words exhausted!")
    return None


def fetch_and_save_word():
    today = datetime.date.today().isoformat()

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM words WHERE created_at = ?", (today,)).fetchone()
    conn.close()
    if existing:
        print(f"Word for today already exists: {existing['word']}")
        return dict(existing)

    used_words = get_used_words()
    data = pick_new_word(used_words)

    if not data:
        print("Failed to pick a new word today.")
        return None

    insert_word(data)
    return data


def get_latest_word():
    conn = get_db_connection()
    word = conn.execute("SELECT * FROM words ORDER BY created_at DESC LIMIT 1").fetchone()
    conn.close()
    return dict(word) if word else None


if __name__ == "__main__":
    result = fetch_and_save_word()
    if result:
        print("\n✅ Today's word:", result["word"])
        print("   Meaning: ", result["meaning"])
        print("   Example: ", result["example"])
        print("   Synonyms:", result["synonyms"] or "none")
        print("   Antonyms:", result["antonyms"] or "none")
        print("   Phonetic:", result["phonetic"] or "none")