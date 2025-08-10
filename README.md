# DailyDrop – Word of the Day App

DailyDrop is a Flask-based application that automatically fetches a new **word of the day** from a free dictionary API, stores it in a database to avoid repetition, and displays it on a beautiful webpage.  
It also sends daily emails containing the word, meaning, pronunciation, synonyms, antonyms, and example usage.

---

## Features

- **Automated Word Fetching** – Uses a free dictionary API to get a new word every day.
- **No Repeats** – Tracks previously used words in the database.
- **Pronunciation Audio** – Includes audio links when available.
- **Daily Email** – Sends the word to subscribed users every morning.
- **Web Dashboard** – Shows the word of the day and all words from the current week.
- **Secure Credentials** – Uses `.env` file to store email credentials, etc.
- **Free Hosting** – Designed to work on PythonAnywhere.

## Tech Stack

- **Backend** – Python, Flask
- **Database** – SQLite
- **Frontend** – HTML, CSS (Tailwind optional)
- **Email** – SMTP with Python `smtplib`
- **Deployment** – PythonAnywhere

## Project Structure
```

daily\_drop/
├── static/
│   └── style.css
├── templates/
│   └── index.html
├── app.py
├── db.sqlite3
├── fetch\_word.py
├── daily_job.py
├── send\_email.py
├── .env
└── requirements.txt

````

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dhyana369/DailyDrop.git
   cd DailyDrop
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create `.env` file** with:

   ```
   EMAIL_ADDRESS=...
   EMAIL_PASSWORD=...
   ```

4. **Run locally**
   ```bash
   python app.py
   ```

## How It Works

1. **Every day** at a set time, `fetch_word.py` runs and stores a new word in `db.sqlite3`.
2. `send_email.py` sends the word to subscribers.
3. The **webpage** shows the latest word and a list of weekly words.

## Deployment on PythonAnywhere

1. Upload all project files to PythonAnywhere.
2. Set up the **Flask app** in the PythonAnywhere dashboard.
3. Schedule `fetch_word.py` and `send_email.py` via PythonAnywhere **Scheduled Tasks**.
4. Your app is live for public access!

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

