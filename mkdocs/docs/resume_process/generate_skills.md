
**4. Create `docs/resume_process/generate_skills.md`:**

```markdown
# Generate Skills List (Final Stage)

Generates the final list of "hard skills" based on *all* answers provided by the user across all stages. The client
application is responsible for collecting and combining these answers.

### Request

    POST | /api/v001/resume/label/generate

question - вопрос, который задан пользователю
answer - ответ пользователя на вопрос
```json
[
  {
    "question": "What is your most recent job title?",
    "answer": "My most recent job title was Senior Software Engineer."
  },
  {
    "question": "What were your key responsibilities in that role?",
    "answer": "I led the backend team, designed microservices, and improved database performance."
  }
]
```

## Response

```json
[
  {
    "label": "Hard skills",
    "value": "c++, Python, Django, PostgreSQL, Docker, AWS lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
  },
  {
    "label": "Telegram",
    "value": "example"
  },
  {
    "label": "Github",
    "value": "example.git"
  }
]
```
!!! Note
    The generated skills depend on the AI model's analysis of the provided answers. The example above is illustrative.
    
```json
{
  "error": "Answers cannot be empty for final resume generation."
}
```
```json
{
  "error": "Failed to generate resume skills. Please try again later."
}
```


