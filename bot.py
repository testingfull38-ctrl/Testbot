# bot.py
# Random Telegram Bot with Flask (Render-ready)
# Replace TELEGRAM_TOKEN in Render env vars with your bot token

import os
import requests
from flask import Flask, request, jsonify
import random
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ✅ SAFE WAY (recommended for Render)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ⚠️ QUICK TEST (uncomment this line if env var doesn't work, but NOT safe)
# TOKEN = "8385389366:AAGBlr4iANz5i6MxJjNgodhugGmhIdlCaOY"

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN env var is required")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

JOKES = [
    "Why did the programmer quit his job? Because he didn't get arrays. 😅",
    "Why do bees have sticky hair? Because they use honeycombs. 🐝",
    "I told my computer I needed a break — it said: 'No problem, I'll go to sleep.' 💻😴",
    "Why did the tomato blush? Because it saw the salad dressing. 🍅😳"
]

HELP_TEXT = (
    "Hey! I'm your Random Bot 🤖\n\n"
    "Commands:\n"
    "/start - Welcome message\n"
    "/help - This message\n"
    "/joke - Hear a random joke\n"
    "/coin - Flip a coin\n"
    "/rand <n> - Random number between 1 and n\n"
    "/echo <text> - I'll repeat what you say\n\n"
    "Or just send any text and I'll reply randomly. 🎲"
)

def send_message(chat_id: int, text: str, reply_to_message_id: int = None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)

@app.route("/", methods=["GET"])
def index():
    return "✅ Random Telegram Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True})

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    msg_id = message.get("message_id")

    # Commands
    if text.startswith("/start"):
        send_message(chat_id, "Welcome! I'm Random Bot 🚀", msg_id)
    elif text.startswith("/help"):
        send_message(chat_id, HELP_TEXT, msg_id)
    elif text.startswith("/joke"):
        send_message(chat_id, random.choice(JOKES), msg_id)
    elif text.startswith("/coin"):
        send_message(chat_id, f"Coin flip: {random.choice(['Heads 🪙','Tails 🪙'])}", msg_id)
    elif text.startswith("/rand"):
        parts = text.split()
        try:
            n = int(parts[1])
            send_message(chat_id, f"Random number (1–{n}): {random.randint(1,n)}", msg_id)
        except:
            send_message(chat_id, "Usage: /rand <number>", msg_id)
    elif text.startswith("/echo"):
        send_message(chat_id, text.partition(" ")[2] or "Usage: /echo <text>", msg_id)
    else:
        choice = random.choice([
            random.choice(JOKES),
            f"You said: {text}",
            f"Random number: {random.randint(1,100)}",
            f"Coin flip: {random.choice(['Heads','Tails'])}"
        ])
        send_message(chat_id, choice, msg_id)

    return jsonify({"ok": True})

def set_webhook():
    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not external_url:
        return
    webhook_url = f"https://{external_url}/{TOKEN}"
    requests.post(f"{TELEGRAM_API}/setWebhook", json={"url": webhook_url})

if __name__ == "__main__":
    set_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
