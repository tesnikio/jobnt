#!/usr/bin/env python
import logging
import config

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.constants import ParseMode, ChatAction

from telegram.ext import (
    filters,
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
)


logger = logging.getLogger(__name__)


async def start_handle(update: Update, context: CallbackContext):
    welcome_text = """
                    Hello! I'm <b>jobnt</b> bot created to help you get your dream job referral or to bless someone with the one 🔗\n\n<i>Please choose one of the options from a menu ⬇️</i>
                   """

    reply_keyboard = [["refer me", "i can refer"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        welcome_text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def initial_choice_handle(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if user_choice == "refer me":
        await refer_me_handle(update, context)
    elif user_choice == "i can refer":
        await i_can_refer_handle(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that choice.")


async def refer_me_handle(update: Update, context: CallbackContext):
    # TODO: load list of companies into keyboard buttons from a db
    keyboard = [
        [InlineKeyboardButton("Apple", callback_data="apple")],
        [InlineKeyboardButton("Google", callback_data="google")],
        [InlineKeyboardButton("OpenAI", callback_data="openai")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose company you wanna work for:", reply_markup=reply_markup
    )


async def refer_me_button_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Extract the callback data
    data = query.data

    # Process based on callback data
    if data == "apple":
        # Replace this with real data or a function call to get data
        employee_list = "Tim Cook, Steve Jobs, etc."
        await query.edit_message_text(f"People working at Apple: {employee_list}")
    elif data == "google":
        # Similar handling for Google
        pass
    elif data == "openai":
        # Similar handling for OpenAI
        pass
    else:
        await query.edit_message_text("Unknown option selected")


# TODO: implement this later
async def i_can_refer_handle(update: Update, context: CallbackContext):
    # Add your logic for "i can refer" option here
    await update.message.reply_text(
        "You selected 'i can refer'. Let's proceed with that."
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.telegram_token).build()

    application.add_handler(CommandHandler("start", start_handle))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, initial_choice_handle)
    )
    application.add_handler(CallbackQueryHandler(refer_me_button_handle))

    application.run_polling()
