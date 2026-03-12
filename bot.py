from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

BUY_LINK = "https://yourwebsite.com"
CONTACT_LINK = "https://t.me/yourusername"

async def add_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.channel_post:
        message = update.channel_post

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🛒 Buy Now", url=BUY_LINK),
                InlineKeyboardButton("📩 Contact", url=CONTACT_LINK)
            ]
        ])

        await context.bot.edit_message_reply_markup(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reply_markup=keyboard
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, add_buttons))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
