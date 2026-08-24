import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---- നിങ്ങളുടെ വിവരങ്ങൾ നൽകുക ----
BOT_TOKEN = '8850071921:AAE085nHB0iW0hIPi1Ih_pY2EV1-ZprAM3o'
MY_USER_ID = 1415979751  # ഇവിടെ നിങ്ങളുടെ USER_ID നൽകുക

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Send me any Instagram link, and I will download the video for you.')

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    url = update.message.text.strip()

    # മറ്റുള്ളവർ അയക്കുന്ന ലിങ്കുകൾ നിങ്ങളുടെ ഐഡിയിലേക്ക് അയക്കുന്നു
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
        await status_msg.edit_text("Could not download the video. Please ensure the link is from a public account.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    app.run_polling()
