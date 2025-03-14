from fastapi import FastAPI, Body
from pydantic import BaseModel
import requests

app = FastAPI(
    title="Resume Generator Microservice",
    description="Микросервис для генерации резюме с помощью нейросети (пример).",
    version="1.0.0",
)

# ------------ НАСТРОЙКИ ------------
API_KEY = "some-key"  # заменить на ваш ключ
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Это ваш "system"-промпт, который служит "контекстом" для нейросети
SYSTEM_PROMPT = """Ты профессиональный HR-ассистент для IT-сферы. Составь раздел "Навыки" резюме на основе ответа пользователя, соблюдая правила:

1. Извлекай ТОЛЬКО профессиональные навыки программиста:
   - Языки, фреймворки, библиотеки
   - Инструменты и платформы
   - Технологии и парадигмы
   - Специализации (ML, WebDev и т.д.)

2. Игнорируй любую другую информацию (цифры, бытовые умения, личные качества)

3. Группируй по категориям. Названия категорий на русском.

4. Формат:
   - Четкие пункты без глаголов
   - Без шаблонных фраз ("Опыт работы", "Уверенное владение")
   - Максимальная конкретность

Если навыков не найдено: "Укажите профессиональные навыки (языки, технологии, инструменты)".
"""

# ------------ ФИКСИРОВАННЫЕ ВОПРОСЫ ------------
# Допустим, у нас есть около 10 базовых вопросов,
# которые мы задаём пользователю про его опыт:
BASE_QUESTIONS = [
    "Сколько лет вы занимаетесь программированием?",
    "С какими языками программирования работали?",
    "Какие используете фреймворки/библиотеки?",
    "Есть ли у вас опыт разработки бэкенда?",
    "Есть ли у вас опыт фронтенда?",
    "Занимались ли вы DevOps-задачами?",
    "Работали ли с системами контроля версий (Git и т.д.)?",
    "Приходилось ли взаимодействовать с базами данных?",
    "У вас есть опыт работы с микросервисной архитектурой?",
    "Есть ли у вас опыт в сфере Machine Learning, Data Science?",
]

# ------------ Pydantic-модели ------------
class UserAnswers(BaseModel):
    # Можно оставить одно поле со всеми ответами сразу
    # или уточнять структуру подробнее
    answers: dict

class UpdateRequest(BaseModel):
    # Предположим, что пользователь шлёт нам текущее "резюме"
    # плюс какую-то новую информацию, которую нужно учитывать
    current_text: str
    new_info: str

# ------------ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ЗАПРОСА К AI ------------
def call_neural_network(user_content: str) -> str:
    """
    Отправляет user_content к модели на openrouter.ai
    и возвращает текст ответа.
    """
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    response = requests.post(API_URL, json=data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        # Обработка ошибок по необходимости
        return f"Ошибка: {response.status_code}, {response.text}"

# ------------ ENDPOINTS ------------
@app.get("/questions")
def get_base_questions():
    """
    Возвращает список базовых вопросов, которые задаются пользователю.
    """
    return {"questions": BASE_QUESTIONS}


@app.post("/generate")
def generate_resume(user_answers: UserAnswers = Body(...)):
    """
    Принимает ответы пользователя (answers) и формирует результат от нейросети.
    Результат отдаем в формате { label: answer }.
    """
    # Собираем все ответы в один общий текст:
    user_text = ""
    for key, value in user_answers.answers.items():
        user_text += f"{key}: {value}\n"

    # Вызываем нейросеть
    nn_response = call_neural_network(user_text)

    # Допустим, мы хотим отдать результат
    # (В реальном случае вы бы ещё сделали парсинг под нужные поля)
    return {
        "experience": "Ваш опыт, извлеченный из ответов",
        "hard_skills": nn_response,
        # Можно добавлять любые нужные поля
    }


@app.post("/update")
def update_resume(update_req: UpdateRequest):
    """
    Принимает текущий текст + новую информацию и отдает новый результат.
    Не храним состояние (сессии нет),
    работаем только с текущим текстом + новой информацией.
    """
    # Склеиваем:
    updated_content = update_req.current_text + "\n" + update_req.new_info

    # Снова вызываем нейросеть с уже обновлённым текстом
    nn_response = call_neural_network(updated_content)

    return {
        "updated_hard_skills": nn_response
    }


# ------------ Запуск сервера ------------
# Запуск через: uvicorn main:app --host 0.0.0.0 --port 8000