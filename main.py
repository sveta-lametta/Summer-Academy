# Импорты
import os
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Настройка Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Загружаем JSON из переменной окружения
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Bahratal_bot").sheet1  # Замени на актуальное название таблицы

# Стадии диалога
NAME, AGE, GENDER, COUNTRY, Q1, Q2, Q3 = range(7)

# Варианты ответов
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

# Обработчики состояний
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
    await update.message.reply_text("В какой стране ты живешь сейчас?")
    return COUNTRY

async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["country"] = update.message.text
    await update.message.reply_text(
        "1. Как ты чувствуешь себя в компании других людей (выбери максимально подходящий вариант, не нужно писать свой)?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_q1, one_time_keyboard=True, resize_keyboard=True),
    )
    return Q1

async def get_q1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q1"] = update.message.text
    await update.message.reply_text(
        "2. Как ты отдыхаешь (выбери максимально подходящий вариант, не нужно писать свой)?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard_q2, one_time_keyboard=True, resize_keyboard=True),
    )
    return Q2

async def get_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["q2"] = update.message.text
    await update.message.reply_text(
        "3. Как ты ведёшь себя в новой группе (выбери максимально подходящий вариант, не нужно писать свой)?",
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

# Главная функция запуска бота
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
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
from sklearn.preprocessing import LabelEncoder

def create_age_group(age, bins=[0, 18, 25, 35, 50, 65, 200], labels=None):
    if labels is None:
        labels = ["0-17", "18-24", "25-34", "35-49", "50-64", "65+"]
    return pd.cut(age, bins=bins, labels=labels, right=False)

def rebalance_groups(df, n_groups=4, max_diff=1):
    """
    Попытка сбалансировать группы по размеру с допуском max_diff.
    Перемещает случайных участников из больших групп в маленькие.
    """
    df = df.copy()
    counts = df["group"].value_counts()
    while counts.max() - counts.min() > max_diff:
        group_max = counts.idxmax()
        group_min = counts.idxmin()

        candidates = df[df["group"] == group_max]
        idx_to_move = candidates.sample(1).index[0]
        df.at[idx_to_move, "group"] = group_min

        counts = df["group"].value_counts()
    return df

def distribute_to_groups_balanced(gsheet_client, sheet_name="Bahratal_bot", target_sheet="Groups", n_groups=4):
    print("Старт функции distribute_to_groups_balanced")

    # Получаем данные
    sheet = gsheet_client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    print(f"Получено {len(df)} записей")

    if len(df) < n_groups:
        print("Недостаточно участников для формирования групп.")
        return

    # Обработка возраста
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df.dropna(subset=["age"], inplace=True)

    # Заполняем пропуски в категориальных
    for col in ["gender", "country", "q1", "q2", "q3"]:
        df[col] = df[col].fillna("Не указано").astype(str)

    # Кодируем ответы (если нужны)
    for col in ["q1", "q2", "q3"]:
        df[col] = LabelEncoder().fit_transform(df[col])

    # Создаем возрастные группы
    df["age_group"] = create_age_group(df["age"])

    # Заполняем пропуски после категоризации возраста
    df["age_group"] = df["age_group"].cat.add_categories("Не указано").fillna("Не указано")

    # Создаем стратификационный ключ
    df["strata"] = df["country"] + "_" + df["age_group"].astype(str) + "_" + df["gender"]

    # Инициализируем колонку с группами
    df["group"] = -1

    # Равномерно распределяем по группам в каждой страти
    for strata_value, group_df in df.groupby("strata"):
        indices = group_df.index.to_list()
        np.random.shuffle(indices)
        for i, idx in enumerate(indices):
            df.at[idx, "group"] = i % n_groups

    # Балансируем группы по размеру (допустимая разница в 1 человека)
    df = rebalance_groups(df, n_groups=n_groups, max_diff=1)

    # Удаляем вспомогательные колонки
    df.drop(columns=["age_group", "strata"], inplace=True)

    # Сохраняем в Google Sheets
    try:
        sh = gsheet_client.open(sheet_name)
        try:
            worksheet_to_delete = sh.worksheet(target_sheet)
            sh.del_worksheet(worksheet_to_delete)
            print(f"Лист '{target_sheet}' удалён")
        except Exception as e:
            print(f"Лист '{target_sheet}' не найден для удаления: {e}")

        new_ws = sh.add_worksheet(title=target_sheet, rows=str(len(df) + 10), cols="20")
        print(f"Лист '{target_sheet}' создан")

        new_ws.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"Данные записаны в лист '{target_sheet}'")
    except Exception as e:
        print("Ошибка при сохранении групп:", e)

    print("Группы успешно распределены и сохранены.")


    
        

distribute_to_groups_balanced(client)

print("=== Скрипт завершён ===")


if __name__ == "__main__":
    main()
