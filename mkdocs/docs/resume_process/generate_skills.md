
**4. Create `docs/resume_process/generate_skills.md`:**

```markdown
# Generate Skills List (Final Stage)

Generates the final list of "hard skills" based on *all* answers provided by the user across all stages. The client application is responsible for collecting and combining these answers.

### Request

```http
    POST | /api/v001/resume/label/generate
    
{
  "answers": [
    "My most recent job title was Senior Software Engineer.",
    "I led the backend team, designed microservices, and improved database performance.",
    "Python, Django, PostgreSQL, Docker, AWS.",
    "A challenging role in a fast-paced environment focused on cloud technologies.",
    "Designed authentication and notification services using FastAPI.",
    "Primarily EC2, S3, RDS, and Lambda.",
    "Optimized complex SQL queries and implemented caching strategies, reducing query time by 40%."
  ]
}

```json
{
  "hard_skills": [
    "Python",
    "Django",
    "FastAPI",
    "PostgreSQL",
    "SQL Query Optimization",
    "Caching Strategies",
    "Microservices Architecture",
    "Docker",
    "AWS (EC2, S3, RDS, Lambda)",
    "Backend Development",
    "Team Leadership"
  ]
}
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


