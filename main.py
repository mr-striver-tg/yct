import logging
from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace this with your actual bot token
BOT_TOKEN = '8125889296:AAFpdhuo75wSBPQFk60-4m0P52P1hmbxWAI'

def start(update, context):
    update.message.reply_text('Welcome! Send /getbook <book_id> to get your YCT PDF link.')

def fetch_pdf_link(book_id):
    url = f"https://yctpublication.com/ebook-detail/{book_id}"
    headers = { "User-Agent": "Mozilla/5.0" }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to find iframe with PDF preview
        iframe = soup.find("iframe", src=True)
        if iframe and "pdf" in iframe['src']:
            return iframe["src"]

        # Fallback: find any PDF link in anchor tags
        for a in soup.find_all("a", href=True):
            if a['href'].lower().endswith(".pdf"):
                return a['href']

        return None
    except Exception as e:
        print(f"Error fetching book: {e}")
        return None

def getbook(update, context):
    if not context.args:
        update.message.reply_text("❗ Usage: /getbook <book_id>")
        return

    book_id = context.args[0]
    update.message.reply_text(f"📖 Fetching book ID {book_id}...")

    pdf_url = fetch_pdf_link(book_id)

    if pdf_url:
        update.message.reply_text(f"✅ Here is your PDF link:\n{pdf_url}")
    else:
        update.message.reply_text("❌ PDF link not found. Try another book ID.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getbook", getbook))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
