# Delete Resume

## API

```
    DELETE| api/v001/user/resume/{id}
```

### Response:

??? success "Статус 204 — Успешное выполнение запроса"

??? warning "Статус 404 — резюме не найдено"

```json
{
  "error": "Not Found"
}

```

??? warning "Статус 401 — невалидный токен"

```json
{
  "error": "Unauthorized"
}
```



