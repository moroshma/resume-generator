# delete user info

### Request

```http
    DELETE| api/v001/users/info
```

### Response:

??? success "Статус 200 — Успешное выполнение запроса"

```json
{
  "education": [
    1,
    2,
    3
  ],
  "experience": [
    1,
    2,
    3
  ],
  "languages": [
    1,
    2,
    3,
    4
  ]
}
```



??? warning "Статус 400 — Ошибка валидации"

```json
{
  "error": "validate error"
}
```
