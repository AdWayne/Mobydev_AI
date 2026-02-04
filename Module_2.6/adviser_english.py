import os, sqlite3, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
FILE_PROMPT = BASE_DIR / "prompt.txt"
FILE_WELCOME = BASE_DIR / "welcome.txt"
FILE_HELP = BASE_DIR / "help.txt"

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

PROMPT_TEMPLATE = load_text(FILE_PROMPT)
WELCOME = load_text(FILE_WELCOME)
HELP_TEXT = load_text(FILE_HELP)

load_dotenv()
client = OpenAI(api_key=os.getenv("API"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# База данных
DB = sqlite3.connect("adviser_english.db")
DB.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL
)""")
DB.commit()

def save(role: str, content: str):
    DB.execute("INSERT INTO sessions (role, content) VALUES (?, ?)", (role, content))
    DB.commit()

def fetch_all():
    return DB.execute("SELECT role, content FROM sessions").fetchall()

def clear_history():
    DB.execute("DELETE FROM sessions")
    DB.commit()

def print_slow(text: str, delay: float = 0.003):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def build_memory() -> str:
    rows = fetch_all()
    if not rows:
        return "История пуста."
    lines = []
    for role, content in rows:
        who = "Пользователь" if role == "user" else "Ассистент"
        lines.append(f"{who}: {content}")
    return "\n".join(lines)

SESSION_VERSION = 0

def ask_llm(user_q: str) -> str:
    rows = fetch_all()

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — наставник по английскому языку. "
                "НЕ повторяй предыдущие упражнения или объяснения. "
                "Развивай тему дальше. Учитывай прошлый контекст."
            )
        }
    ]

    for role, content in rows:
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_q})

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=400,
    )

    return resp.choices[0].message.content.strip()

def main():
    global SESSION_VERSION
    print_slow(WELCOME)

    while True:
        try:
            q = input("\nТы: ").strip()
        except KeyboardInterrupt:
            print("\nВыход. Пока!")
            break

        if not q:
            continue

        low = q.lower()

        if low in ("выход", "/exit", "exit"):
            print("Выход. Пока!")
            break

        if low == "/help":
            print(HELP_TEXT)
            save("assistant", HELP_TEXT)
            continue

        if low == "/reset":
            SESSION_VERSION += 1
            print_slow("Ассистент: Начинаем заново. Укажи свой уровень английского.")
            save("assistant", "Сессия сброшена.")
            continue

        if low == "/delete":
            clear_history()
            SESSION_VERSION = 0
            print("История удалена.")
            continue

        save("user", q)

        print("Ассистент думает...", end='', flush=True)
        for _ in range(3):
            time.sleep(0.25)
            print(".", end='', flush=True)
        print()

        ans = ask_llm(q)
        print_slow(f"Ассистент: {ans}")
        save("assistant", ans)

if __name__ == "__main__":
    main()
