import os
import csv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Стадии диалога
NAME, AGE, GENDER, COUNTRY, Q1, Q2, Q3 = range(7)

user_data_list = []

reply_keyboard_q1 = [
    ["Предпочитаю общаться с 1-2 людьми или быть один"],
    ["Чувствую себя нормально и в одиночку, и в компании"],
    ["Люблю быть среди людей, легко завожу знакомства"],
]

reply_keyboard_q2 = [
    ["Читаю книгу или смотрю фильм дома"],
    ["Встречаюсь с друзьями на прогулке"],
    ["Ищу новые приключения и активности"],
]

reply_keyboard_q3 = [
    ["Стараюсь наблюдать, пока не привыкну к группе"],
    ["Стараюсь быстро завести пару знакомств"],
    ["Активно включаюсь в разговор и знакомлюсь со всеми"],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Давай начнём. Как тебя зовут? (имя, фамилия)")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Сколько тебе лет?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Твой пол? (м/ж/другое)")
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text
    await update.message.reply_text("Из какой ты страны?")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country"] = update.message.text
    await update.message.reply_text(
        "1. Как ты чувствуешь себя в компании других людей?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_q1, one_time_keyboard=True, resize_keyboard=True),
    )
    return Q1

async def get_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q1"] = update.message.text
    await update.message.reply_text(
        "2. Как ты отдыхаешь?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_q2, one_time_keyboard=True, resize_keyboard=True),
    )
    return Q2

async def get_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q2"] = update.message.text
    await update.message.reply_text(
        "3. Как ты ведёшь себя в новой группе?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_q3, one_time_keyboard=True, resize_keyboard=True),
    )
    return Q3

async def get_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q3"] = update.message.text

    # Отправка данных в Google Sheets
    values = [
        context.user_data.get("name", ""),
        context.user_data.get("age", ""),
        context.user_data.get("gender", ""),
        context.user_data.get("country", ""),
        context.user_data.get("q1", ""),
        context.user_data.get("q2", ""),
        context.user_data.get("q3", ""),
    ]
    sheet.append_row(values)

    await update.message.reply_text("Спасибо! Ты успешно прошёл тест 🌟")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос прерван.")
    return ConversationHandler.END

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Ошибка: не найден токен в переменной окружения BOT_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_q1)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_q2)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_q3)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
#дальше для работы с json
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Загружаем JSON из переменной окружения
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    creds_dict = json.loads(creds_json)

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Открываем таблицу по имени
    sheet = client.open("Название твоей таблицы").sheet1
    return sheet
