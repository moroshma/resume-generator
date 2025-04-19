# delete user info

### Request

```http
    DELETE| api/v001/users/info
```

### Request:

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


### Response:

??? success "Статус 204 — Успешное выполнение запроса"


??? warning "Статус 400 — Ошибка валидации"

```json
{
  "error": "validate error"
}
```
