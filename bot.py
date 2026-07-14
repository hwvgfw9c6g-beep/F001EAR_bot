import os
import re
import sqlite3
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)


TOKEN = AAHlAEodjSrQmo-cnPQ4JOkjIiFwNilIvU8

CHANNEL_ID = -1003514787630


PREFIXES = (
    "903",
    "905",
    "906",
    "909",
    "960",
    "961",
    "962",
    "963",
    "964",
    "965",
    "967",
    "968",
    "991"
)


LIMIT = 10


# -----------------
# База
# -----------------

conn = sqlite3.connect(
    "numbers.db",
    check_same_thread=False
)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS numbers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
number TEXT UNIQUE,
username TEXT
)
""")

conn.commit()



# -----------------
# Поиск номеров
# -----------------

def extract_numbers(text):

    if not text:
        return []

    found = re.findall(
        r"\d{10,11}",
        text
    )

    result = []

    for n in found:
        if n.startswith(PREFIXES):
            result.append(n)

    return result



# -----------------
# Добавление
# -----------------

def save_number(number, username):

    cur.execute(
        """
        INSERT OR IGNORE INTO numbers
        (number, username)
        VALUES (?,?)
        """,
        (
            number,
            username
        )
    )

    conn.commit()



def get_all():

    cur.execute(
        """
        SELECT number, username
        FROM numbers
        ORDER BY id
        LIMIT 10
        """
    )

    return cur.fetchall()



def clear_numbers():

    cur.execute(
        "DELETE FROM numbers"
    )

    conn.commit()



# -----------------
# Обработка сообщений
# -----------------

async def handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return


    text = (
        update.message.text
        or
        update.message.caption
    )


    numbers = extract_numbers(text)


    if not numbers:
        return



    user = update.message.from_user


    if user.username:
        username = "@" + user.username
    else:
        username = "нет_username"



    for number in numbers:

        save_number(
            number,
            username
        )



    saved = get_all()



    if len(saved) >= LIMIT:


        message = ""


        for number, user in saved:

            message += (
                f"{user} — {number}\n"
            )


        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=message
        )


        clear_numbers()



# -----------------
# Запуск
# -----------------

app = Application.builder()\
    .token(TOKEN)\
    .build()


app.add_handler(
    MessageHandler(
        filters.TEXT |
        filters.CAPTION,
        handler
    )
)


print("BOT STARTED")


app.run_polling()
