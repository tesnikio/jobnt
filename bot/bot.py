#!/usr/bin/env python
import logging
import config

from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    filters,
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)


logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: CallbackContext):
    welcome_text = """
                    Hello! I'm <b>jobnt</b> bot created to help you get your dream job referral or to bless someone with the one 🔗\n\n<i>Please choose one of the options from a menu⬇️</i>
                   """

    reply_keyboard = [["refer me", "i can refer"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        welcome_text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def handle_choice(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if user_choice == "refer me":
        await handle_refer_me(update, context)
    elif user_choice == "i can refer":
        await handle_i_can_refer(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that choice.")


async def handle_refer_me(update: Update, context: CallbackContext):
    # Add your logic for "refer me" option here
    await update.message.reply_text("You selected 'refer me'. Let's proceed with that.")


async def handle_i_can_refer(update: Update, context: CallbackContext):
    # Add your logic for "i can refer" option here
    await update.message.reply_text(
        "You selected 'i can refer'. Let's proceed with that."
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.telegram_token).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)
    )

    application.run_polling()
