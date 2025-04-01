from pydantic import BaseModel

class UserAnswers(BaseModel):
    answers: dict

class UpdateRequest(BaseModel):
    current_text: str
    new_info: str
