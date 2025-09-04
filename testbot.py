import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
import asyncio

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DEVNET_BOT_TOKEN = os.getenv("DEVNET_BOT_TOKEN")
MONITORING_BOT_TOKEN = os.getenv("MONITORING_BOT_TOKEN")
MONITORING_CHAT_ID = "7445514748"  # Your Telegram chat ID
SENDER_PRIVATE_KEY = os.getenv("SENDER_PRIVATE_KEY")

# Solana Devnet client
SOLANA_CLIENT = Client("https://api.devnet.solana.com")
LAMPORTS_PER_SOL = 1_000_000_000  # 1 SOL = 1 billion lamports

# Initialize sender keypair
try:
    sender_keypair = Keypair.from_bytes(eval(SENDER_PRIVATE_KEY))
except Exception as e:
    logger.error(f"❌ Error loading sender keypair: {e}")
    raise SystemExit("Invalid SENDER_PRIVATE_KEY in environment variables")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command for Devnet Bot."""
    keyboard = [
        [InlineKeyboardButton("Send SOL 🚀", callback_data="send_sol")],
        [InlineKeyboardButton("Check Balance 💰", callback_data="check_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌟 Welcome to Solana Devnet Bot!\n"
        "Choose an action below to send SOL or check your wallet balance.",
        reply_markup=reply_markup
    )
    await send_monitoring_message(f"🔔 User {update.effective_user.id} started the Devnet Bot.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses for Devnet Bot."""
    query = update.callback_query
    await query.answer()

    if query.data == "send_sol":
        await query.message.reply_text(
            "📨 Enter the recipient's Solana address and amount (in SOL):\n"
            "Example: /send <address> <amount>"
        )
    elif query.data == "check_balance":
        balance = get_wallet_balance(sender_keypair.pubkey())
        await query.message.reply_text(f"💰 Wallet balance: {balance / LAMPORTS_PER_SOL:.2f} SOL")
        await send_monitoring_message(
            f"📊 User {update.effective_user.id} checked balance: {balance / LAMPORTS_PER_SOL:.2f} SOL"
        )

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /send command to transfer SOL on Devnet."""
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("❌ Usage: /send <recipient_address> <amount_in_sol>")
            return

        recipient_address = args[0]
        amount_sol = float(args[1])
        amount_lamports = int(amount_sol * LAMPORTS_PER_SOL)

        # Validate recipient address
        try:
            recipient_pubkey = Pubkey.from_string(recipient_address)
        except ValueError:
            await update.message.reply_text("❌ Invalid Solana address!")
            return

        # Create and send transaction
        transaction = Transaction().add(
            transfer(TransferParams(
                from_pubkey=sender_keypair.pubkey(),
                to_pubkey=recipient_pubkey,
                lamports=amount_lamports
            ))
        )
        response = SOLANA_CLIENT.send_transaction(transaction, sender_keypair)
        tx_hash = response.value

        await update.message.reply_text(
            f"✅ Transaction sent! 🎉\n"
            f"View on Explorer: https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
        )
        await send_monitoring_message(
            f"💸 User {update.effective_user.id} sent {amount_sol:.2f} SOL to {recipient_address}\n"
            f"Tx Hash: https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Transaction failed: {str(e)}")
        await send_monitoring_message(
            f"🚨 Transaction error by user {update.effective_user.id}: {str(e)}"
        )

def get_wallet_balance(pubkey: Pubkey) -> int:
    """Get wallet balance in lamports."""
    try:
        response = SOLANA_CLIENT.get_balance(pubkey)
        return response.value
    except Exception as e:
        logger.error(f"❌ Failed to get balance: {e}")
        return 0

async def send_monitoring_message(message: str) -> None:
    """Send a message to the Monitoring Bot."""
    try:
        app = Application.builder().token(MONITORING_BOT_TOKEN).build()
        await app.bot.send_message(chat_id=MONITORING_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"❌ Failed to send monitoring message: {e}")

async def monitoring_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command for Monitoring Bot."""
    await update.message.reply_text(
        "🔔 Solana Devnet Monitoring Bot is active! 📡\n"
        "You'll receive updates on Devnet Bot activities here."
    )

def main() -> None:
    """Run both bots."""
    # Devnet Bot
    devnet_app = Application.builder().token(DEVNET_BOT_TOKEN).build()
    devnet_app.add_handler(CommandHandler("start", start))
    devnet_app.add_handler(CommandHandler("send", send))
    devnet_app.add_handler(CallbackQueryHandler(button_callback))

    # Monitoring Bot
    monitoring_app = Application.builder().token(MONITORING_BOT_TOKEN).build()
    monitoring_app.add_handler(CommandHandler("start", monitoring_start))

    # Start both bots
    logger.info("🚀 Starting Devnet and Monitoring Bots...")
    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            devnet_app.run_polling(),
            monitoring_app.run_polling()
        )
    )

if __name__ == "__main__":
    main()
