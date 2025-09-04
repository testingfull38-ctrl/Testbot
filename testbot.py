# 🔗 LinkShortenerBot - Shorten your links with style ✨
# ✅ Single script with internal logging system

import requests
import datetime
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔑 Main Bot Token (for users)
BOT_TOKEN = "8385389366:AAEmM-MPUUGVDsUVIQEZ_RNMgd355eUc2c8"

# 🔑 Logging Bot Token (used only for sending logs)
LOG_BOT_TOKEN = "8266266158:AAGAa16y--lN5UzgxmUKFmkI1ymJf-o8ylI"

# 🆔 Chat ID where logs should be sent (your Telegram account or group)
LOG_CHAT_ID = "7445514748"

# 🔑 Bitly API Key
BITLY_API_KEY = "3409ca54dcba37a7c0caf1e6f15cd24471257bad"

# 🌐 Bitly API Endpoint
BITLY_API_URL = "https://api-ssl.bitly.com/v4/shorten"

# 📌 Helper function: Send logs to your log chat
async def log_activity(message: str):
    log_bot = Bot(LOG_BOT_TOKEN)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    await log_bot.send_message(
        chat_id=LOG_CHAT_ID,
        text=f"📝 *Log* ({timestamp}):\n{message}",
        parse_mode="Markdown",
    )

# 📌 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "👋 Hi there! I’m *LinkShortenerBot* 🤖\n\n"
        "Paste a long link and I’ll make it short & neat 🔗✨\n\n"
        "👉 Try /help to learn how to use me.",
        parse_mode="Markdown",
    )
    await log_activity(f"User @{user.username} ({user.id}) started the bot.")

# 📌 /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "❓ *How to use me*\n\n"
        "➡️ Send: `/shorten https://example.com`\n"
        "➡️ I’ll reply with a short Bitly link ⚡️\n\n"
        "💡 Tip: You can send me any valid URL.",
        parse_mode="Markdown",
    )
    await log_activity(f"User @{user.username} ({user.id}) requested /help.")

# 📌 /shorten command
async def shorten_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    url = " ".join(context.args)

    if not url:
        await update.message.reply_text(
            "⚠️ Please provide a link!\n\nExample:\n`/shorten https://example.com`",
            parse_mode="Markdown",
        )
        await log_activity(f"User @{user.username} ({user.id}) used /shorten without a URL.")
        return

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    headers = {"Authorization": f"Bearer {BITLY_API_KEY}", "Content-Type": "application/json"}
    data = {"long_url": url}
    response = requests.post(BITLY_API_URL, headers=headers, json=data)

    if response.status_code == 200:
        short_url = response.json()["link"]
        await update.message.reply_text(
            f"✅ Success! Here’s your short link:\n\n🔗 {short_url}"
        )
        await log_activity(f"User @{user.username} ({user.id}) shortened {url} → {short_url}")
    else:
        await update.message.reply_text("❌ Oops! Something went wrong. Please try again later.")
        await log_activity(f"⚠️ ERROR: Failed to shorten {url} for @{user.username} ({user.id})")

# 📌 Log all other messages (non-commands)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    await log_activity(f"User @{user.username} ({user.id}) sent a message: {text}")

# 🚀 Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers (scheduler configuration removed)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("shorten", shorten_url))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
