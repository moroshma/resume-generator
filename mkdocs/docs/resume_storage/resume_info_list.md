# resume info list 

## API

```
    GET|api/v001/user/resume/list
```


### Response:

??? success "Статус 200 — Успешное выполнение запроса"


```json
[
  {
    "resume_id": 1,
    "user_id": 101,
    "created_at": "2023-01-01T12:00:00Z",
    "title": "Software Engineer.pdf"
  },
  {
    "resume_id": 2,
    "user_id": 102,
    "created_at": "2023-02-01T12:00:00Z",
    "title": "Data Scientist.pdf"
  },
  {
    "resume_id": 3,
    "user_id": 103,
    "created_at": "2023-03-01T12:00:00Z",
    "title": "Product Manager.pdf"
  },
  {
    "resume_id": 4,
    "user_id": 104,
    "created_at": "2023-04-01T12:00:00Z",
    "title": "UX Designer.pdf"
  },
  {
    "resume_id": 5,
    "user_id": 105,
    "created_at": "2023-05-01T12:00:00Z",
    "title": "DevOps Engineer.pdf"
  }
]
```

??? warning "Статус 401 — невалидный токен"

```json
{
  "error": "Unauthorized"
}
```



