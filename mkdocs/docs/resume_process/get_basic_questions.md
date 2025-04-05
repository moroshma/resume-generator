# Get Basic Questions (Stage 1)

Retrieves the initial list of base questions for the resume generation process.

### Request

```http
    GET | /api/v001/resume/basic/question

```json
{
  "questions": [
    "What is your most recent job title?",
    "What were your key responsibilities in that role?",
    "What are your primary technical skills?",
    "What are you looking for in your next role?"
  ]
}
```
!!! Note
    The actual questions are defined in the application configuration (`settings.BASE_QUESTIONS`). The example above is illustrative.
    
```json
{
  "error": "Unauthorized"
}
```

```json
{
  "error": "Internal server error"
}
```


