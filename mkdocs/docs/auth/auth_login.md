# LOGIN

## sing in

## API

```
    POST| api/v001/auth/login
```

### Request

```json
{
  "email": "string",
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

??? warning "Статус 401 — Неверный логин или пароль"

```json
{
  "error": "Unauthorized"
}
```



