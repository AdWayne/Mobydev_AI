import os
import json
import csv
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIQuizGenerator:
    def __init__(self, seed=42):
        self.client = OpenAI(api_key=os.getenv("API"))
        self.seed = seed
        random.seed(self.seed)
        self.questions = []
        self.score = 0

    def generate_quiz(self, topic, count=5, q_type="mixed"):
        type_instruction = {
            "1": "Use only 'multiple' choice questions with 4 options.",
            "2": "Use only 'open' questions (no options, direct text answer).",
            "3": "Mix both 'multiple' and 'open' questions."
        }
        
        selected_instruction = type_instruction.get(q_type, type_instruction["3"])

        prompt = f"""
        Generate a quiz about '{topic}'. 
        Count: {count} questions. 
        Style: {selected_instruction}
        Format: Return ONLY a JSON object with a key 'quiz' containing a list of objects.
        Each object:
        - 'question': text
        - 'type': 'multiple' or 'open'
        - 'options': list of 4 strings (null if open)
        - 'answer': correct string value
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a professional quiz creator. Output only valid JSON."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        raw_data = json.loads(response.choices[0].message.content)
        self.questions = raw_data['quiz']
        
        for q in self.questions:
            if q['type'] == 'multiple' and q['options']:
                random.shuffle(q['options'])
        
        self.save_structure()

    def save_structure(self, filename="quiz.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=4)

    def start(self):
        report_data = []
        
        for i, q in enumerate(self.questions):
            print(f"\nВопрос {i+1}: {q['question']}")
            
            user_answer = ""
            if q['type'] == 'multiple':
                for idx, opt in enumerate(q['options']):
                    print(f"{idx + 1}. {opt}")
                
                choice = input("Ваш ответ (номер): ")
                try:
                    user_answer = q['options'][int(choice) - 1]
                except:
                    user_answer = choice
            else:
                user_answer = input("Ваш ответ: ")

            is_correct = user_answer.strip().lower() == q['answer'].strip().lower()
            
            if is_correct:
                print("Верно!")
                self.score += 1
            else:
                print(f"Ошибка. Правильный ответ: {q['answer']}")
            
            report_data.append({
                "Question": q['question'],
                "Your Answer": user_answer,
                "Correct Answer": q['answer'],
                "Result": "Correct" if is_correct else "Wrong"
            })

        self.save_report(report_data)

    def save_report(self, data, filename="report.csv"):
        if not data: return
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        
        print(f"\nИтог: {self.score}/{len(self.questions)}")
        print(f"Результаты сохранены в quiz.json и report.csv")

if __name__ == "__main__":
    quiz_app = AIQuizGenerator()
    
    topic = input("Введите тему викторины: ")
    count = input("Количество вопросов: ")
    
    print("\nВыберите тип вопросов:")
    print("1 - Только тест (выбор варианта)")
    print("2 - Только открытые вопросы")
    print("3 - Смешанные")
    q_choice = input("Ваш выбор: ")
    
    quiz_app.generate_quiz(topic, count=int(count), q_type=q_choice)
    quiz_app.start()