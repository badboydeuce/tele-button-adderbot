import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)

# ────────────────────────────────────────────────
# Logging setup (very useful on Render)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# Configuration – change these values
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

BUY_LINK = "https://yourwebsite.com"           # ← replace
CONTACT_LINK = "https://t.me/yourusername"     # ← replace or keep @yourusername

# Optional: add a secret path to make webhook harder to guess (recommended)
WEBHOOK_PATH = "/secret-bot-path"              # change this to something random

# ────────────────────────────────────────────────
async def add_channel_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add Buy Now + Contact buttons to new channel posts"""
    if not update.channel_post:
        return

    message = update.channel_post

    # Skip service messages, pinned messages, etc.
    if (
        message.left_chat_member
        or message.new_chat_members
        or message.pinned_message
        or message.channel_chat_created
    ):
        return

    # Optional: only react to messages that have text or caption
    if not (message.text or message.caption):
        return

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛒 Buy Now", url=BUY_LINK),
            InlineKeyboardButton("📩 Contact", url=CONTACT_LINK),
        ]
    ])

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reply_markup=keyboard
        )
        logger.info(f"Buttons added to channel post {message.message_id} in {message.chat.title}")
    except Exception as e:
        logger.error(f"Failed to edit message {message.message_id}: {e}")


async def set_webhook_on_startup(application: Application) -> None:
    """Set or update webhook when the bot starts"""
    port = int(os.getenv("PORT", "8443"))
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")

    if not hostname:
        logger.error("RENDER_EXTERNAL_HOSTNAME not found → webhook cannot be set")
        return

    webhook_url = f"https://{hostname}{WEBHOOK_PATH}"

    try:
        await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True   # optional: clear queue on restart
        )
        logger.info(f"Webhook successfully set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handler only for channel posts
    application.add_handler(
        MessageHandler(filters.UpdateType.CHANNEL_POST, add_channel_buttons)
    )

    # Set webhook automatically when the app starts
    application.post_init = set_webhook_on_startup

    # Webhook settings for Render
    port = int(os.getenv("PORT", "8443"))

    logger.info(f"Starting webhook server on port {port}")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=WEBHOOK_PATH,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}",
        # Optional: if you get SSL errors or want to skip cert verification (not recommended)
        # drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()