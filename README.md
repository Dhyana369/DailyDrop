# DailyDrop – Word of the Day App

DailyDrop is a Flask-based application that automatically fetches a new **word of the day** using the **Merriam-Webster API**, stores it in a database to avoid repetition, and displays it on a clean, aesthetic webpage.  
It also sends daily emails containing the word, meaning, pronunciation, synonyms, antonyms, and an example sentence.

---

## Features

- **Fully Automated Word Fetching** – Picks a random English word daily and validates it against the Merriam-Webster Collegiate Dictionary. No manual word list needed — runs forever on autopilot.
- **No Repeats** – Tracks all previously used words in the database so the same word is never sent twice.
- **Complete Word Data** – Every word includes a definition, example sentence, synonyms, antonyms, and phonetic pronunciation sourced from Merriam-Webster.
- **Pronunciation Audio** – Includes a playable audio button on the webpage using the Merriam-Webster audio API.
- **Daily Email** – Sends a beautifully designed HTML email to all subscribers every morning matching the webpage design.
- **Web Dashboard** – Displays today's word with full details and a "This Week" section showing the past 7 days as clickable cards.
- **Subscribe / Unsubscribe** – Users can subscribe via the webpage and unsubscribe via a link in the email.
- **Secure Credentials** – Uses a `.env` file to store all sensitive keys and credentials.
- **Free Hosting** – Designed to run on PythonAnywhere with a scheduled daily task.

---

## Tech Stack

- **Backend** – Python, Flask
- **Database** – SQLite
- **Frontend** – HTML, CSS (custom, no frameworks)
- **Dictionary API** – Merriam-Webster Collegiate Dictionary + Thesaurus
- **Email** – SMTP with Python `smtplib`
- **Deployment** – PythonAnywhere

---

## Project Structure

```
DailyDrop/
├── templates/
│   └── index.html        # Webpage UI
├── app.py                # Flask app and routes
├── fetch_word.py         # Word fetching logic (MW API)
├── daily_job.py          # Runs fetch + send every day
├── send_email.py         # Email sending logic
├── requirements.txt      # Python dependencies
├── .env                  # Secret credentials (not committed)
└── db.sqlite3            # SQLite database (not committed)
```

---

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dhyana369/DailyDrop.git
   cd DailyDrop
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** with:
   ```
   GMAIL_USER=your@gmail.com
   GMAIL_PASSWORD=your_app_password
   MW_DICT_KEY=your_merriam_webster_dictionary_key
   MW_THESAURUS_KEY=your_merriam_webster_thesaurus_key
   ```

   - Get your free Merriam-Webster API keys at [dictionaryapi.com](https://dictionaryapi.com)
   - Use a Gmail App Password (not your regular password)

4. **Run locally**
   ```bash
   python app.py
   ```

5. **Fetch today's word manually**
   ```bash
   python fetch_word.py
   ```

6. **Test the full daily job (fetch + email)**
   ```bash
   python daily_job.py
   ```

---

## How It Works

1. Every day at a scheduled time, `daily_job.py` runs automatically on PythonAnywhere.
2. It calls `fetch_word.py` which:
   - Picks a random English word via a random word API
   - Validates it against the **Merriam-Webster Dictionary API** — must have a definition and example sentence
   - Fetches synonyms and antonyms from the **Merriam-Webster Thesaurus API**
   - Saves the complete word data to `db.sqlite3`
3. It then calls `send_email.py` which sends a complete HTML email to all subscribers.
4. The **webpage** at `dhyana.pythonanywhere.com` shows today's word and this week's words via Flask routes.

---

## Deployment on PythonAnywhere

1. Upload all project files to `/home/YourUsername/daily_drop/`
2. Set up the **Flask app** in the PythonAnywhere Web tab
3. Add your `.env` keys via the Files tab
4. Run the DB migration once in the Bash console:
   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('db.sqlite3')
   for col, defn in [('part_of_speech', 'TEXT DEFAULT \"\"'), ('phonetic', 'TEXT DEFAULT \"\"')]:
       try:
           conn.execute(f'ALTER TABLE words ADD COLUMN {col} {defn}')
           print(f'Added: {col}')
       except: print(f'Skipped: {col}')
   conn.commit()
   "
   ```
5. Schedule `daily_job.py` via PythonAnywhere **Tasks** tab (recommended: 2:30 UTC = 8:00 AM IST)
6. Reload the web app — your site is live!

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

