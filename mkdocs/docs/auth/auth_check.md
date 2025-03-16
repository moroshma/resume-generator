# check auth

## API

```
    GET| api/v001/auth/check
```

### Response:

??? success "Статус 204 — Успешное выполнение запроса"

??? warning "Статус 401 — невалидный токен"

```json
{
  "error": "Unauthorized"
}
```



