from fastapi import APIRouter, Body
from ai_service.services.neural import NeuralService
from ai_service.schemas.resume import UserAnswers, UpdateRequest
from ai_service.config import settings

router = APIRouter(tags=["Resume Generation"])
neural_service = NeuralService(settings)

@router.get("/questions")
async def get_base_questions():
    return {"questions": settings.BASE_QUESTIONS}

@router.post("/generate")
async def generate_resume(user_answers: UserAnswers = Body(...)):
    return neural_service.process_answers(user_answers.answers)

@router.post("/update")
async def update_resume(update_req: UpdateRequest):
    return neural_service.update_resume(
        update_req.current_text,
        update_req.new_info
    )
