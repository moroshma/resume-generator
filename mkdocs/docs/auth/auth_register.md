# REGISTER

## Register a new user

### Request

```http
    POST| api/v001/auth/register
```


```json
{
  "login": "string",
  "password": "string"
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

??? warning "Статус 409 — Пользователь с таким email уже существует"

```json
{
  "error": "User already exists"
}
```