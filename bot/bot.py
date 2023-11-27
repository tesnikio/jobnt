#!/usr/bin/env python
import logging
import config
import database

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
db = database.Database()


async def start_handle(update: Update, context: CallbackContext):
    welcome_text = """
                    Hello! I'm <b>jobnt</b> bot created to help you get your dream job referral or to bless someone with the one 🔗\n\n<i>Please choose one of the options from a menu ⬇️</i>
                   """

    reply_keyboard = [["refer me", "i can refer"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        welcome_text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def message_handle(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if user_choice == "refer me":
        await refer_me_handle(update, context)
    elif user_choice == "i can refer":
        await i_can_refer_handle(update, context)
    elif context.user_data.get("awaiting_company_name"):
        incoming_message = update.message.text

        company_name, position_title = incoming_message.split(", ")

        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name

        db.add_new_user(
            user_id, username, first_name, last_name, company_name, position_title
        )

        await update.message.reply_text(
            "Thank you! Your information has been saved and will be shown in a list of referrers 🤗"
        )

        del context.user_data["awaiting_company_name"]
    else:
        await update.message.reply_text(
            "Sorry, I was unable to recognize the option you've chosen."
        )


async def refer_me_handle(update: Update, context: CallbackContext):
    users = db.get_all_users()

    keyboard = []

    for user in users:
        user_company_name = user["company_name"]
        keyboard.append(
            [InlineKeyboardButton(user_company_name, callback_data=user_company_name)]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "List of available companies:", reply_markup=reply_markup
    )


async def refer_me_button_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    selected_company_name = query.data

    employee_list = db.get_all_users()

    selected_company_employees = [
        user for user in employee_list if user["company_name"] == selected_company_name
    ]

    message = f"<b>People working at {selected_company_name}:</b>\n"

    for employee in selected_company_employees:
        first_name = employee["first_name"]
        last_name = employee["last_name"]
        position_title = employee["position_title"]
        contact = employee["username"]
        message += f"{first_name} {last_name}, {position_title}, {contact}\n"

    if selected_company_name:
        await query.edit_message_text(message, parse_mode=ParseMode.HTML)
    else:
        await query.edit_message_text("Unknown option selected")


async def i_can_refer_handle(update: Update, context: CallbackContext):
    message = f"Please enter <i>the name of the company</i> you can refer to and <i>your position</i> title at this company in the following format:\n\n<b>Company, Position</b>\n"
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
    )
    context.user_data["awaiting_company_name"] = True


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.telegram_token).build()

    application.add_handler(CommandHandler("start", start_handle))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle)
    )
    application.add_handler(CallbackQueryHandler(refer_me_button_handle))

    application.run_polling()
