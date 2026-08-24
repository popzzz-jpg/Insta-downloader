import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render ഡെപ്ലോയ്‌മെന്റ് പരാജയപ്പെടാതിരിക്കാൻ ഒരു ചെറിയ വെബ് സെർവർ
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# ---- നിങ്ങളുടെ വിവരങ്ങൾ നൽകുക ----
BOT_TOKEN = 'ഇവിടെ_നിങ്ങളുടെ_BOT_TOKEN_നൽകുക'
MY_USER_ID = 123456789  # നിങ്ങളുടെ USER ID നൽകുക

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Send me any Instagram link, and I will download the video for you.')

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    url = update.message.text.strip()

    if user_id != MY_USER_ID:
        log_txt = f"🔔 **New Link Received!**\n👤 User: @{username} (`{user_id}`)\n🔗 Link: {url}"
        try:
            await context.bot.send_message(chat_id=MY_USER_ID, text=log_txt, parse_mode='Markdown')
        except Exception:
            pass

    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram link.")
        return

    status_msg = await update.message.reply_text("Downloading video, please wait...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'insta_{user_id}_%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="Here is your video!")

        if os.path.exists(filename):
            os.remove(filename)

        await status_msg.delete()

    except Exception:
        await status_msg.edit_text("Could not download video. Make sure the link is from a public post.")

if __name__ == '__main__':
    # വെബ് സെർവർ ബാക്ക്ഗ്രൗണ്ടിൽ റൺ ചെയ്യുന്നു
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # ടെലിഗ്രാം ബോട്ട് റൺ ചെയ്യുന്നു
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    app.run_polling()
