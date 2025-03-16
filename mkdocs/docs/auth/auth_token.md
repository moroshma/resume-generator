## refresh token

# refresh access token by refresh token

## API

```
    GET| v001/api/auth/token/refresh
```

### Response:

??? success "Статус 204 — Успешное выполнение запроса"

??? warning "Статус 401 — невалидный токен"

```json
{
  "error": "Unauthorized"
}
```



