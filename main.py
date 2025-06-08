import logging
from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace this with your actual Telegram Bot Token
BOT_TOKEN = '8125889296:AAFpdhuo75wSBPQFk60-4m0P52P1hmbxWAI'

# Start command
def start(update, context):
    update.message.reply_text("👋 Welcome! Use /getbook <book_id> to fetch a YCT eBook preview link.")

# Function to fetch PDF preview link
def fetch_pdf_link(book_id):
    try:
        url = f"https://yctpublication.com/ebook-detail/{book_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # First, try to find an iframe (used for preview PDF)
        iframe = soup.find('iframe')
        if iframe and 'src' in iframe.attrs:
            return iframe['src']

        # Second, try to find <a> links that contain .pdf
        for a in soup.find_all("a", href=True):
            if ".pdf" in a['href']:
                return a['href']

        return None

    except Exception as e:
        logger.error(f"Error fetching PDF for book ID {book_id}: {e}")
        return None

# Command: /getbook <book_id>
def getbook(update, context):
    if not context.args:
        update.message.reply_text("❗ Please provide a Book ID.\nUsage: /getbook 2582")
        return

    book_id = context.args[0].strip()
    update.message.reply_text(f"🔍 Fetching book ID {book_id}...")

    pdf_link = fetch_pdf_link(book_id)

    if pdf_link:
        update.message.reply_text(f"✅ Here is your eBook preview:\n{pdf_link}")
    else:
        update.message.reply_text("❌ PDF link not found. Please try another Book ID.")

# Main bot setup
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getbook", getbook))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
