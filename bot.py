# bot.py
import logging
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Set up logging to track bot activity and errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token (use environment variable for security)
TOKEN = os.getenv("TOKEN", "8266266158:AAGekMGM1yw91G9zBd08z9c7kMyecMG_Kws")  # Fallback for local testing

# Sample data for bot responses
jokes = [
    "Why did the scarecrow become a programmer? He was outstanding in his field! 😄",
    "Why don't eggs tell jokes? They'd crack up! 🥚",
    "What do you call a dinosaur that brushes its teeth? A Flossiraptor! 🦖"
]

facts = [
    "The shortest war lasted 38 minutes! ⏱️",
    "Octopuses have three hearts and can change color! 🐙",
    "Honey never spoils, even in ancient tombs! 🍯"
]

# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message with an emoji-based interactive menu."""
    # Define the inline keyboard with emoji buttons
    keyboard = [
        [
            InlineKeyboardButton("😺 Joke", callback_data='joke'),
            InlineKeyboardButton("🚀 Fact", callback_data='fact'),
        ],
        [InlineKeyboardButton("❓ Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send welcome message with the menu
    await update.message.reply_text(
        "Welcome to Emoji Bot! 🎉\nChoose an option:",
        reply_markup=reply_markup
    )

# Handler for button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button clicks and sends appropriate responses."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    choice = query.data
    if choice == 'joke':
        await query.message.reply_text(random.choice(jokes))
    elif choice == 'fact':
        await query.message.reply_text(random.choice(facts))
    elif choice == 'help':
        await query.message.reply_text(
            "I'm Emoji Bot! 😊\n"
            "Use /start to see the menu.\n"
            "Click 😺 for a joke, 🚀 for a fact, or ❓ for this help message."
        )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs errors for debugging."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Sets up and runs the bot."""
    # Initialize the bot application
    application = Application.builder().token(TOKEN).build()

    # Register command and button handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(error_handler)

    # Start polling for updates
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
