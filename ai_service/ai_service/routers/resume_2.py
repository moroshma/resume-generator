from fastapi import APIRouter, Body, HTTPException, status, Response

from ai_service.services.neural_1 import NeuralService
from ai_service.services.pdf_generator import PDFResumeGenerator
from ai_service.services.pdf_generator import create_resume_pdf

from ai_service.schemas.resume_1 import (
    UserAnswers,
    UpdateRequest,
    QuestionsResponse,
    GeneratedSkillsResponse,
    UpdatedSkillsResponse
)

from ai_service.config import settings

router = APIRouter(tags=["Resume Generation"])

neural_service = NeuralService(settings)

@router.get("/api/v001/resume/basic/question", response_model=QuestionsResponse)
async def get_base_questions():

    return {"questions": settings.BASE_QUESTIONS}

@router.post("/api/v001/resume/question/get", response_model=QuestionsResponse)
async def get_next_questions(user_answers: UserAnswers = Body(...)):

    if not user_answers.answers:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty when requesting follow-up questions.",
        )
    try:
        follow_up_questions = await neural_service.generate_follow_up_questions(user_answers.answers)
        return {"questions": follow_up_questions}
    except Exception as e:
        print(f"Error in /next-questions endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate follow-up questions. Please try again later.",
        )

@router.post("/api/v001/resume/label/generate", response_model=GeneratedSkillsResponse)
async def generate_resume_final(user_answers: UserAnswers = Body(...)):
    if not user_answers.answers:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty for final resume generation.",
        )
    try:
        result = await neural_service.process_answers(user_answers.answers)
        return result
    except Exception as e:
        print(f"Error in /generate endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate resume skills. Please try again later.",
        )

@router.post("/api/v001/resume/label/regenerate", response_model=UpdatedSkillsResponse)
async def update_resume_section(update_req: UpdateRequest = Body(...)):
    try:
        result = await neural_service.update_resume(
            update_req.current_text,
            update_req.new_info
        )
        return result
    except Exception as e:
        print(f"Error in /update endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update resume section. Please try again later.",
        )

@router.post("/api/v001/resume/pdf/generate")
async def generate_resume_pdf(user_answers: UserAnswers = Body(...)):

    if not user_answers.answers:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty for PDF generation.",
        )

    try:
        skills_result = await neural_service.process_answers(user_answers.answers)
        generated_skills = skills_result.get("hard_skills", [])

        pdf_bytes = create_resume_pdf(user_answers.answers, generated_skills)
        pdf_bytes = bytes(pdf_bytes)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume_summary.pdf"
            }
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in /generate-pdf endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate resume PDF. Please try again later.",
        )
