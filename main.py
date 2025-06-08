import os
import tempfile
import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes
from telegram import Update, InputMediaPhoto, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext

# === CONFIGURATION ===
BOT_TOKEN = '8125889296:AAFpdhuo75wSBPQFk60-4m0P52P1hmbxWAI'  # Replace with your actual bot token
BASE_URL = 'https://yctbook.com/bookdetails/'

# === HELPER FUNCTION TO GET PDF LINK ===
def get_pdf_url(book_id):
    try:
        url = BASE_URL + str(book_id)
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            return iframe['src']
        
        for a in soup.find_all('a', href=True):
            if a['href'].lower().endswith('.pdf'):
                return a['href']
    except Exception as e:
        print(f"Error fetching book page: {e}")
    return None

# === MAIN COMMAND HANDLER ===
def getbook(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❗ Please provide a book ID.\nUsage: /getbook 1431")
        return

    book_id = context.args[0]
    update.message.reply_text(f"🔍 Fetching book ID {book_id}...")

    pdf_url = get_pdf_url(book_id)
    if not pdf_url:
        update.message.reply_text("❌ PDF link not found. Try another book ID.")
        return

    try:
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        update.message.reply_text(f"❗ Failed to download PDF: {str(e)}")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(response.content)
        pdf_path = tmp_pdf.name

    try:
        # Send the PDF
        update.message.reply_text("📤 Sending PDF file...")
        context.bot.send_document(chat_id=update.effective_chat.id, document=InputFile(pdf_path))

        # Convert first 3 pages to images
        images = convert_from_bytes(response.content, dpi=200, first_page=1, last_page=3)
        media_group = []

        for img in images:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                img.save(tmp_img.name, "PNG")
                media_group.append(InputMediaPhoto(media=open(tmp_img.name, 'rb')))

        if media_group:
            update.message.reply_media_group(media=media_group)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error during processing: {e}")
    finally:
        # Clean up
        try:
            os.remove(pdf_path)
        except: pass

# === SETUP TELEGRAM BOT ===
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("getbook", getbook))
    print("✅ Bot started.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
