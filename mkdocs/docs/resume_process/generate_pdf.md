
**6. Create `docs/resume_process/generate_pdf.md`:**

```markdown
# Generate Resume PDF

Generates a resume summary PDF file based on *all* answers provided by the user across all stages. This endpoint internally generates the skills list and then creates the PDF.

### Request

```http
    POST | /api/v001/resume/pdf/generate
    
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


**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename=resume_summary.pdf
```
The browser will typically prompt the user to download the file named `resume_summary.pdf`.

```json
{
  "error": "Answers cannot be empty for PDF generation."
}
```
```json
{
  "error": "Unauthorized"
}
```
```json
{
  "error": "Failed to generate resume PDF. Please try again later."
}
```
