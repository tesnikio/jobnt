#!/usr/bin/env python
import logging
import config
import database
from utils import validate_format, is_email

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
                    Hello! I'm <b>jobnt</b> 🤖 created to help you get your dream job referral or to bless someone with the one 🔗\n\n🔻 Click <b>refer me</b> to see list of companies and people that are ready to refer you.\n\n🔻 Click <b>i can refer</b> if you're can give a referral to the company you work for. You will be asked to provide your contact information, such as an email address or Telegram handle, so that individuals interested in referral opportunities can reach out to you.\n\n🔻 Click <b>remove my profile</b> if you don't want to be in the list of referres.\n\nDon't be jobn't 😎\n\n<i>Please choose one of the options from a menu ⬇️</i>
                   """

    reply_keyboard = [["🙏 refer me", "🙋 i can refer", "🗑️ remove my profile"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(
        welcome_text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def message_handle(update: Update, context: CallbackContext):
    incoming_message = update.message.text

    is_valid, err = validate_format(incoming_message)

    if "refer me" in incoming_message:
        await refer_me_handle(update, context)
    elif "i can refer" in incoming_message:
        await i_can_refer_handle(update, context)
    elif "remove my profile" in incoming_message:
        await remove_profile_handle(update, context)
    elif context.user_data.get("awaiting_company_name") and is_valid:
        company_name, position_title = incoming_message.split(", ")

        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name

        db.add_new_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            position_title=position_title,
        )

        await update.message.reply_text(
            "Thank you! Your information has been saved and will be shown in a list of referrers 🤗"
        )

        contact_keyboard = [
            [InlineKeyboardButton("📲 Telegram", callback_data="contact_telegram")],
            [InlineKeyboardButton("📧 Email", callback_data="contact_email")],
        ]
        reply_markup = InlineKeyboardMarkup(contact_keyboard)
        await update.message.reply_text(
            "How would you like to be contacted?", reply_markup=reply_markup
        )

        del context.user_data["awaiting_company_name"]
    elif is_email(incoming_message):
        db.update_user_email(update.effective_user.id, incoming_message)
        await update.message.reply_text(
            "Great, your email has been added to your profile ✅"
        )
    else:
        await update.message.reply_text(
            "Sorry, incorrect message format or wrong message 🚫"
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
        "🏢 List of available companies:"
        if keyboard
        else "Sorry, there's no available companies for referrals 😔",
        reply_markup=reply_markup,
    )


async def refer_me_button_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "contact_telegram":
        await query.edit_message_text(
            "Great, your handle has been added to your profile ✅",
            parse_mode=ParseMode.HTML,
        )
    elif query.data == "contact_email":
        await query.edit_message_text(
            "Please, enter your email ⬇️",
            parse_mode=ParseMode.HTML,
        )
    else:
        selected_company_name = query.data

        employee_list = db.get_all_users()

        selected_company_employees = [
            user
            for user in employee_list
            if user["company_name"] == selected_company_name
        ]

        message = f"<b>🧑‍💻 working at {selected_company_name}:</b>\n\n"

        for employee in selected_company_employees:
            first_name = employee["first_name"]
            last_name = employee["last_name"]
            position_title = employee["position_title"]
            telegram_handle = employee["username"]
            email = employee["email"]

            if email:
                message += f"🔘 <b>{first_name} {last_name}</b>, <i>{position_title}</i>, <b>Email</b>: {email}\n\n"
            else:
                message += f"🔘 <b>{first_name} {last_name}</b>, <i>{position_title}</i>, <b>Telegram</b>: @{telegram_handle}\n\n"

        if selected_company_name:
            await query.edit_message_text(message, parse_mode=ParseMode.HTML)
        else:
            await query.edit_message_text("Unknown option selected")


async def i_can_refer_handle(update: Update, context: CallbackContext):
    message = "✍️ Please enter ***the name of the company*** you can refer to and ***your position title*** at this company in the following format:\n\n```Format Company, Position```\n"
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
    )
    context.user_data["awaiting_company_name"] = True


async def remove_profile_handle(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if db.check_if_user_exists(user_id):
        db.remove_user_by_id(user_id)
        message = "Your information has been removed from the list of referrers 👋"
    else:
        message = "There's no information about you, nothing to remove."

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.telegram_token).build()

    application.add_handler(CommandHandler("start", start_handle))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handle)
    )
    application.add_handler(CallbackQueryHandler(refer_me_button_handle))

    application.run_polling()
