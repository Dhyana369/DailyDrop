import logging
import traceback
from fetch_word import fetch_and_save_word, get_latest_word
from send_email import send_email_to_all

# Debug logging setup
logging.basicConfig(
    filename='/home/Dhyana/daily_drop/daily_drop_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def log_exception(e):
    logging.error(f"Exception: {e}")
    logging.error(traceback.format_exc())

logging.info("=== DEBUG RUN STARTED ===")

try:
    logging.debug("Fetching and saving word...")
    word_data = fetch_and_save_word()
    logging.debug(f"Word data after fetch: {word_data}")

    if not word_data:
        logging.info("No new word inserted today, fetching latest word from DB...")
        word_data = get_latest_word()
        logging.debug(f"Word data from DB: {word_data}")

    if word_data:
        logging.info(f"Preparing to send emails for word: {word_data['word']}")
        try:
            # Intercept recipient list for debug
            from send_email import get_all_recipients  # you must have this function or similar
            recipients = get_all_recipients()
            logging.info(f"Total recipients: {len(recipients)}")
            for r in recipients:
                logging.debug(f"Recipient: {r}")

            send_email_to_all(word_data)  # Send emails as usual
            logging.info("send_email_to_all() finished without raising an exception.")

        except Exception as e:
            log_exception(e)
    else:
        logging.warning("No word data available to send.")

except Exception as e:
    log_exception(e)

logging.info("=== DEBUG RUN COMPLETED ===")
