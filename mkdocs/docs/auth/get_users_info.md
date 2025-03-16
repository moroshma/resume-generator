# Get user info

### Request

```http
    GET| api/v001/users/info
```

### Response:

??? success "Статус 200 — Успешное выполнение запроса"

```json
{
  "name": "string",
  "surname": "string",
  "email": "example@gmail.com",
  "github": "moroshma",
  "phone_number": "+780123456789",
  "location": "City, Country",
  "education": [
    {
      "institution": "University Name",
      "degree": "Degree Title",
      "from": "YYYY",
      "to": "YYYY"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "role": "Job Title",
      "from": "YYYY-MM",
      "to": "YYYY-MM",
      "description": "Job responsibilities and achievements"
    }
  ],
  "social_profiles": {
    "linkedin": "https://linkedin.com/in/username",
    "telegram": "@telegram"
  },
  "languages": [
    "Language1",
    "Language2"
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