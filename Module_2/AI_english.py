from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

print("Привет! Я твой репетитор по английскому языку. Как я могу помочь тебе сегодня?")

client = OpenAI(api_key=os.getenv("API"))

reader = PdfReader("Курс по англискому языку.pdf")
course_content = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        course_content += text + "\n"


faqs = [
    {"question": "Что такое Present Simple?", 
     "answer": "Present Simple используется для регулярных действий, фактов и расписаний. Пример: I go to school every day."},

    {"question": "Что такое Present Continuous?", 
     "answer": "Present Continuous используется для действий, происходящих сейчас. Пример: I am studying now."},

    {"question": "В чем разница между Present Simple и Present Continuous?", 
     "answer": "Present Simple — регулярные действия. Present Continuous — действия в данный момент."},

    {"question": "Как образуется Present Simple?", 
     "answer": "Глагол используется в первой форме, но для he/she/it добавляется -s. Пример: She works."},

    {"question": "Как образуется Present Continuous?", 
     "answer": "am/is/are + глагол с окончанием -ing. Пример: They are playing."},

    {"question": "Когда используется Past Simple?", 
     "answer": "Past Simple используется для действий в прошлом. Пример: I visited my friend yesterday."},

    {"question": "Как задать вопрос в Present Simple?", 
     "answer": "Используется do/does в начале. Пример: Do you like coffee?"},

    {"question": "Как сделать отрицание в Present Continuous?", 
     "answer": "am/is/are + not + глагол-ing. Пример: She is not sleeping."},

    {"question": "Что такое неправильные глаголы?", 
     "answer": "Это глаголы, у которых формы прошедшего времени образуются не по правилу. Пример: go – went – gone."},

    {"question": "Что такое артикли a и the?", 
     "answer": "A используется с неисчисляемыми или впервые упоминаемыми объектами, the — когда объект известен."}
]


def ask_llm(user_q: str) -> str:
    faq_text = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in faqs])

    prompt = f"""
Ты — репетитор английского языка.
Используй ТОЛЬКО информацию из курса и FAQ.
Вопрос пользователя: {user_q}

Курс:
{course_content}

FAQ:
{faq_text}

Ответ:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=
        [{"role": "system", "content": "Ты — полезный и дружелюбный репетитор по английскому языку."},
        {"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


def get_answer(user_q: str) -> str:
    answer = ask_llm(user_q)

    if "не знаю" in answer.lower() or "нет информации" in answer.lower():
        return "Извините, я не могу найти ответ в курсе."
    else:
        return answer


while True:
    q = input("Вы: ")

    if q.lower() in ["выход", "exit", "quit"]:
        print("До свидания!")
        break

    print("English_AI:", get_answer(q))