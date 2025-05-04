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
    API_KEY: str = os.getenv("API_KEY", "some-key")

    # --- Annotation [config.py: 4] ---
    # URL of the external LLM service endpoint.
    API_URL: str = os.getenv("API_URL","https://api.groq.com/openai/v1/chat/completions")

    # MODEL

    MODEL_ID: str = os.getenv("MODEL_ID", "deepseek-r1-distill-llama-70b")

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
    SYSTEM_PROMPT: str = """Ты профессиональный HR-ассистент для IT-сферы. Твоя задача - извлечь ключевую информацию из ответов пользователя и представить ее в структурированном виде.

### Правила извлечения:
- Извлекай ТОЛЬКО профессионально значимую информацию: языки программирования, фреймворки, библиотеки, инструменты, платформы, технологии, парадигмы, методологии разработки, области специализации (Backend, Frontend, ML, DevOps и т.д.), ключевые достижения и опыт, релевантный для IT-вакансий.
- **Лейблы (labels)** должны быть краткими, понятными и отражать суть извлеченной информации (например, "Языки программирования", "Фреймворки Backend", "Опыт DevOps", "Ключевые проекты"). Придумывай релевантные лейблы сам, если стандартных не хватает.
- **Значения (values)** должны содержать саму информацию, извлеченную из текста. Это может быть строка или список строк, если уместно (например, для списка языков).
- Игнорируй нерелевантную информацию: общие фразы, личные качества, не относящиеся к IT навыки, хобби.
- Не добавляй информацию, которой нет в ответах пользователя.
- Если из ответов невозможно извлечь никакой полезной информации, верни пустой список `[]`.

### Формат ответа:
- **СТРОГО JSON-список объектов.** Каждый объект в списке должен иметь два ключа: "label" (строка) и "value" (строка или список строк).
- **Пример формата:**
  ```json
  [
    {"label": "Языки программирования", "value": "Python, JavaScript, C++"},
    {"label": "Фреймворки Backend", "value": "Django, "FastAPI"},
    {"label": "Опыт работы", "value": "5 лет коммерческой разработки, включая 2 года на позиции Team Lead."},
    {"label": "Базы данных", "value": "PostgreSQL, Redis"},
    {"label": "Облачные платформы", "value": "AWS (EC2, S3)"}
  ]

-Обязательно используй ДВОЙНЫЕ кавычки для всех строк и ключей в JSON.
-В ответе НЕ ДОЛЖНО БЫТЬ ничего, кроме самого JSON-списка (никаких объяснений, json оберток и т.д.). Ответ должен быть напрямую парсируемым json.loads().
    """

    # --- Annotation [config.py: 7] ---
    # System prompt for the LLM when generating follow-up questions
    # based on the user's initial answers.
    FOLLOW_UP_QUESTIONS_PROMPT: str = """Ты профессиональный HR-ассистент для IT-сферы. Сгенерируй 5-7 уточняющих вопросов СТРОГО по следующим правилам:

### Формат ответа:
- Только JSON-объект с одним ключом "questions", значение которого - массив строк. Пример:
  {"questions": ["Как вы применяли [Технологию X] в проекте Y?", "Опишите архитектуру вашего решения на [Фреймворк Z]?"]}
- Обязательно используй ДВОЙНЫЕ кавычки для строк и ключей.
- Никаких markdown-блоков (```json ```), только чистый JSON.
- Ответ должен быть парсируемым json.loads() без обработки.

### Требования к вопросам:
1. **Конкретика технологий**
   Упоминай технологии из ответов пользователя (Пример: "Как вы использовали FastAPI для оптимизации endpoints?")

2. **Глубина экспертизы**
   Запрашивай детали:
   - Проблемы и их решения ("С какими сложностями столкнулись при внедрении Django ORM?")
   - Архитектурные решения ("Как вы организовали микросервисную коммуникацию?")
   - Инструменты ("Какие библиотеки использовали для тестирования в FastAPI?")

3. **Запрещено**
   - Повторять предыдущие вопросы
   - Общие вопросы без привязки к ответам
   - Упоминать хобби/личностные качества

### Пример ответа:
{"questions": ["Как вы настраивали асинхронные задачи в Django?", "Какие механизмы кеширования применяли в ваших проектах?"]}
    """



    UPDATE_PROMPT: str = """Ты профессиональный HR-ассистент. Твоя задача - обновить предоставленный раздел резюме на основе дополнительной информации от пользователя.
    Входные данные:
    Текущие структурированные данные: Предоставлены в виде текста, описывающего пары label-value.
    Дополнительная информация/инструкции: Текст от пользователя с указаниями, что изменить, добавить или удалить.
    Правила обновления:
    Проанализируй "Дополнительную информацию" и соотнеси ее с "Текущими данными".
    Модифицируй существующие value для соответствующих label, если пользователь дал уточнения или исправления.
    Добавляй новые пары {"label": "...", "value": "..."}, если пользователь предоставил новую релевантную информацию, которой не было. Придумай подходящий label.
    Удаляй существующие пары label-value, если пользователь явно просит об этом или новая информация делает старую неактуальной (на твое усмотрение, если не указано явно).
    Сохраняй те пары label-value из текущих данных, которые не затронуты инструкциями пользователя и все еще релевантны.
    Цель - получить актуальный и полный набор структурированных данных в виде списка.
    Формат ответа:
    СТРОГО JSON-список объектов, точно такой же, как в SYSTEM_PROMPT. Каждый объект в списке должен иметь два ключа: "label" (строка) и "value" (строка или список строк).
    Пример формата:

    [
    {"label": "Языки программирования", "value": "Python, JavaScript, Go"},
    {"label": "Фреймворки Backend", "value": "FastAPI", "Gin Gonic"},
    {"label": "Опыт работы", "value": "6 лет коммерческой разработки, 2 года Team Lead."},
    {"label": "Базы данных", "value": "PostgreSQL, Redis, ClickHouse"},
    {"label": "Контейнеризация", "value": "Docker, Kubernetes"}
    ]

    Обязательно используй ДВОЙНЫЕ кавычки для всех строк и ключей в JSON.
    В ответе НЕ ДОЛЖНО БЫТЬ ничего, кроме самого JSON-списка (никаких объяснений, json оберток и т.д.). Ответ должен быть напрямую парсируемым json.loads().
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
