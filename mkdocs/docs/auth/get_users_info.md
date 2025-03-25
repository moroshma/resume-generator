# Get user info

### Request

```http
    GET| api/v001/users/info
```

### Response:

??? success "Статус 200 — Успешное выполнение запроса"

```json
{
  "user_id": 1,
  "name": "Alexander",
  "surname": "Smith",
  "email": "alex.smith@gmail.commmm",
  "github": "github.com/alexsmith",
  "phone_number": "+1 (555) 123-4567",
  "location": "San Francisco, CA",
  "education": [
    {
      "education_id": 1,
      "institution": "Stanford University",
      "degree": "Master of Science in Computer Science",
      "from": "2018-09",
      "to": "2020-06"
    },
    {
      "education_id": 2,
      "institution": "University of California, Berkeley",
      "degree": "Bachelor of Science in Computer Engineering",
      "from": "2014-09",
      "to": "2018-05"
    }
  ],
  "experience": [
    {
      "experience_id": 1,
      "company": "Google",
      "role": "Senior Software Engineer",
      "from": "2020-07",
      "to": "present",
      "description": "Leading backend development team for Google Cloud Platform. Implementing scalable microservices architecture and improving system performance."
    },
    {
      "experience_id": 2,
      "company": "Twitter",
      "role": "Software Engineer",
      "from": "2018-06",
      "to": "2020-06",
      "description": "Developed and maintained high-traffic RESTful APIs. Implemented real-time data processing pipelines using Apache Kafka."
    }
  ],
  "social_profiles": {
    "linkedin": "linkedin.com/in/alexandersmith",
    "telegram": "@alexsmith"
  },
  "languages": [
    {
      "language_id": 1,
      "language": "English"
    },
    {
      "language_id": 2,
      "language": "Spanish"
    },
    {
      "language_id": 3,
      "language": "Mandarin"
    }
  ]
}
```

??? warning "Статус 400 — Ошибка валидации"

```json
{
  "error": "validate error"
}
```

??? warning "Статус 409 — Пользователь с таким email уже существует"

```json
{
  "error": "User already exists"
}
```