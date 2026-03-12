from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os
import logging

# Enable logging (very helpful when debugging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

BUY_LINK = "https://yourwebsite.com"          # ← change
CONTACT_LINK = "https://t.me/yourusername"    # ← change or keep @yourusername

async def add_channel_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.channel_post:
        return

    message = update.channel_post

    # Optional: skip service messages, pinned messages, etc.
    if message.left_chat_member or message.new_chat_members or message.pinned_message:
        return

    # Optional: only add buttons to messages with text or caption
    if not (message.text or message.caption):
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛒 Buy Now", url=BUY_LINK),
            InlineKeyboardButton("📩 Contact", url=CONTACT_LINK)
        ]
    ])

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reply_markup=keyboard
        )
        logger.info(f"Added buttons to channel post {message.message_id}")
    except Exception as e:
        logger.error(f"Failed to add buttons to {message.message_id}: {e}")

def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Much better filter: only channel posts
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, add_channel_buttons))

    print("Bot is starting... (waiting for new channel posts)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()