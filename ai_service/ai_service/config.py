# config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# --- Annotation [config.py: 1] ---
# Load environment variables from a .env file.
# This allows sensitive information like API keys and service URLs
# to be stored outside the code, which is good practice.
load_dotenv()

class Settings(BaseSettings):
    # --- Annotation [config.py: 2] ---
    # Basic application metadata used by FastAPI for documentation.
    APP_TITLE: str = "Resume Generator Microservice"
    APP_DESCRIPTION: str = "Микросервис для генерации резюме с помощью нейросети"
    APP_VERSION: str = "1.0.0"

    # --- Annotation [config.py: 3] ---
    # API Key specifically for the external LLM service (OpenRouter).
    # Loaded from the 'OPENROUTER_API_KEY' environment variable.
    # Default value "some-key" is provided but should be overridden in .env.
    API_KEY: str = os.getenv("OPENROUTER_API_KEY", "some-key")

    # --- Annotation [config.py: 4] ---
    # URL of the external LLM service endpoint.
    API_URL: str = "https://openrouter.ai/api/v1/chat/completions"

    # --- Annotation [config.py: 5] ---
    # URL of your separate authentication microservice.
    # Loaded from the 'AUTH_SERVICE_URL' environment variable.
    # IMPORTANT: When running in Docker Compose, this should typically be the
    # service name defined in your docker-compose.yml file, e.g.,
    # "http://auth-service/api/v001/user/auth/check".
    # For local testing outside Docker, it might be "http://localhost:PORT/...".
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8081/api/v001/user/auth/check") # Example default

    # --- Annotation [config.py: 6] ---
    # System prompt for the LLM when extracting skills from user answers.
    # Provides instructions and rules for the AI.
    SYSTEM_PROMPT: str = """Ты профессиональный HR-ассистент для IT-сферы. Составь раздел "Навыки" резюме на основе ответа пользователя, соблюдая правила:
### Формат ответа:
- Только JSON-объект с  ключами, подходящими под описание, значения которых - строки. Пример:
    {
        "hard_skills": "C/C++, HTML, CSS, REST API"
        "experience": "Я работал в X компании на позиции... Я сопровождал весь проект от создания до выката в прод..."
        "technologies": "..."
        ...
    }
- Обязательно используй ДВОЙНЫЕ кавычки для строк и ключей.
- Никаких markdown-блоков (```json ```), только чистый JSON.
- Ответ должен быть парсируемым json.loads() без обработки.


### требования к вопросам:

    Извлекай ТОЛЬКО профессиональные навыки программиста:
    Языки, фреймворки, библиотеки
    Инструменты и платформы
    Технологии и парадигмы
    Специализации (ML, WebDev и т.д.)

    Игнорируй любую другую информацию (цифры, бытовые умения, личные качества)
    Группируй по категориям. Названия категорий на русском.
    Формат:
    Четкие пункты без глаголов
    Без шаблонных фраз ("Опыт работы", "Уверенное владение")
    Максимальная конкретность

    Если навыков не найдено: "Укажите профессиональные навыки (языки, технологии, инструменты)".


    """

    # --- Annotation [config.py: 7] ---
    # System prompt for the LLM when generating follow-up questions
    # based on the user's initial answers.
    FOLLOW_UP_QUESTIONS_PROMPT: str = """Ты профессиональный HR-ассистент для IT-сферы. На основе предыдущих ответов пользователя о его опыте и навыках, задай 5-7 дополнительных уточняющих вопросов, чтобы глубже понять его экспертизу. Вопросы должны касаться:

    - Конкретных проектов или задач, где применялись указанные технологии.
    - Глубины знаний в ключевых областях (например, "Расскажите подробнее о вашем опыте с [Технология X]").
    - Опыта решения сложных проблем.
    - Предпочтений в работе или дальнейшего развития.

    Сформулируй вопросы четко и открыто.
    НЕ повторяй вопросы, которые уже были заданы.
    Игнорируй нерелевантную информацию из ответов пользователя (личные качества, хобби и т.д.), фокусируйся только на профессиональном опыте и навыках.
    Верни ТОЛЬКО список вопросов в формате JSON-массива строк. Пример: ["Вопрос 1?", "Вопрос 2?", "Вопрос 3?"]
    """

    # --- Annotation [config.py: 8] ---
    # The initial list of questions (Stage 1) asked to the user.
    BASE_QUESTIONS: list[str] = [ # Explicitly typed as list[str]
        "Сколько лет вы занимаетесь программированием?",
        "С какими языками программирования работали?",
        "Какие используете фреймворки/библиотеки?",
        "Есть ли у вас опыт разработки бэкенда? Если да, то с какими технологиями?",
        "Есть ли у вас опыт фронтенда? Если да, то с какими технологиями?",
        "Занимались ли вы DevOps-задачами? (CI/CD, Docker, Kubernetes и т.д.)",
        "Работали ли с системами контроля версий (Git и т.д.)?",
        "Приходилось ли взаимодействовать с базами данных? Какими именно?",
        "У вас есть опыт работы с микросервисной архитектурой?",
        "Есть ли у вас опыт в сфере Machine Learning, Data Science или других специализированных областях?",
    ]

    # --- Annotation [config.py: 9] ---
    # BaseSettings automatically looks for a .env file,
    # so the inner 'Config' class with env_file is not strictly needed
    # if load_dotenv() is used or if the .env file is in the standard location.
    # class Config:
    #     env_file = ".env"

# --- Annotation [config.py: 10] ---
# Create a single instance of the Settings class.
# This instance will be imported and used throughout the application
# to access configuration values.
settings = Settings()
