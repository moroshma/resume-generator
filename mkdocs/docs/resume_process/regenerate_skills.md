**5. Create `docs/resume_process/regenerate_skills.md`:**

```markdown
# Regenerate/Update Skills Section

Updates an existing text section (e.g., previously generated hard skills) by incorporating new information provided by
the user.

```http
    POST | /api/v001/resume/label/regenerate
```

### Request

```json
{
  "wish": "i want to update my skills section with new information and middle+ golang developer",
  "user_edits": [
    {
      "question": "What is your most recent job title?",
      "answer": "My most recent job title was Senior Software Engineer."
    },
    {
      "question": "What were your key responsibilities in that role?",
      "answer": "I led the backend team, designed microservices, and improved database performance."
    }
  ]
}
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
The updated text reflects the AI model's integration of the new information into the current text. The example above is
illustrative.

```json
{
  "error": "Unauthorized"
}
```

```json
{
  "error": "Failed to update resume section. Please try again later."
}
```
