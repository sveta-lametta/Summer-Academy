# main.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import csv

# Стадии диалога
NAME, AGE, GENDER, COUNTRY, Q1, Q2, Q3 = range(7)

user_data_list = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Давай начнём. Как тебя зовут?")
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
        reply_markup=ReplyKeyboardMarkup([["🐢", "🐍", "🦅"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return Q1

async def get_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q1"] = update.message.text
    await update.message.reply_text(
        "2. Как ты отдыхаешь?",
        reply_markup=ReplyKeyboardMarkup([["🐢", "🐍", "🦅"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return Q2

async def get_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q2"] = update.message.text
    await update.message.reply_text(
        "3. Как ты ведёшь себя в новой группе?",
        reply_markup=ReplyKeyboardMarkup([["🐢", "🐍", "🦅"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return Q3

async def get_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q3"] = update.message.text

    # Сохраняем в глобальный список
    user_data_list.append(context.user_data.copy())

    # Также можно сохранять в CSV
    with open("responses.csv", "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "gender", "country", "q1", "q2", "q3"])
        writer.writerow(context.user_data)

    await update.message.reply_text("Спасибо! Ты успешно прошёл тест 🌟")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос прерван.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

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
