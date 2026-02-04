import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API")
client = OpenAI(api_key=API_KEY)

db = sqlite3.connect("chat.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,role TEXT,content TEXT)""")
db.commit()

def add(role, txt):
    cursor.execute("INSERT INTO users (role, content) VALUES (?, ?)", (role, txt))
    db.commit()

def msgs():
    return [{"role": row[0], "content": row[1]} for row in cursor.execute("SELECT role, content FROM users ORDER BY id")]

print("Мини чат с базой данных. Введите 'exit' для выхода.")
while True:
    try:
        q = input("Вы: ").strip()
    except KeyboardInterrupt:
        print("\nВыход из чата.")
        break

    if q.lower() == "exit":
        print("Выход из чата.")
        break

    if not q:
        continue

    add("user", q)

    history = msgs()

    reply = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history
    )

    answer = reply.choices[0].message.content
    add("assistant", answer)

    print("Бот:", answer, "\n")