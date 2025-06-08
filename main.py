import logging
from telegram.ext import Updater, CommandHandler
import requests

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your Telegram bot token
BOT_TOKEN = '8125889296:AAFpdhuo75wSBPQFk60-4m0P52P1hmbxWAI'

def start(update, context):
    update.message.reply_text(
        "👋 Welcome! Use /getbook <book_id> to fetch a YCT eBook PDF link.\nExample: /getbook 2582"
    )

def fetch_pdf_link(book_id):
    pdf_url = f"https://ebook.yctpublication.com/pdf/{book_id}.pdf"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.head(pdf_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return pdf_url
        else:
            return None
    except Exception as e:
        logger.error(f"Error checking PDF URL for book {book_id}: {e}")
        return None

def getbook(update, context):
    if not context.args:
        update.message.reply_text("❗ Please provide a Book ID.\nUsage: /getbook 2582")
        return

    book_id = context.args[0].strip()
    update.message.reply_text(f"🔍 Fetching book ID {book_id}...")

    pdf_link = fetch_pdf_link(book_id)

    if pdf_link:
        update.message.reply_text(f"✅ Here is your eBook PDF link:\n{pdf_link}")
    else:
        update.message.reply_text(
            "❌ PDF link not found. Please try another Book ID."
        )

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getbook", getbook))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
