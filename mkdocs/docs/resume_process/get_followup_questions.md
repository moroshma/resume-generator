
**3. Create `docs/resume_process/get_followup_questions.md`:**

```markdown
# Get Follow-up Questions (Stage 2)

Generates follow-up questions based on the user's answers to the previous set of questions (e.g., basic questions from Stage 1).

### Request

```http
    POST | /api/v001/resume/question/get
    
{
  "answers": [
    "My most recent job title was Senior Software Engineer.",
    "I led the backend team, designed microservices, and improved database performance.",
    "Python, Django, PostgreSQL, Docker, AWS.",
    "A challenging role in a fast-paced environment focused on cloud technologies."
  ]
}

```json
{
  "questions": [
    "Can you elaborate on the specific microservices you designed?",
    "Which AWS services did you utilize most frequently?",
    "Describe a challenging technical problem you solved related to database performance."
  ]
}
```
!!! Note
    The generated questions depend on the AI model's analysis of the provided answers. The example above is illustrative.
    
```json
{
  "error": "Answers cannot be empty when requesting follow-up questions."
}
```
```json
{
  "error": "Unauthorized"
}
```
```json
{
  "error": "Failed to generate follow-up questions. Please try again later."
}
```
