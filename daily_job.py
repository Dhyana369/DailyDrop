import logging
from fetch_word import fetch_and_save_word, get_latest_word
from send_email import send_email_to_all

logging.basicConfig(
    filename='/home/Dhyana/daily_drop/daily_drop.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

logging.info("Starting daily job...")

word_data = fetch_and_save_word()

if not word_data:
    logging.info("No new word inserted today, fetching latest word from DB...")
    word_data = get_latest_word()

if word_data:
    logging.info(f"Sending emails for word: {word_data['word']}")
    send_email_to_all(word_data)
    logging.info("Emails sent.")
else:
    logging.warning("No word data available to send.")

logging.info("Daily job completed.")
