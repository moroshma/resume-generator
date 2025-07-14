# schemas/resume.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class UserAnswers(BaseModel):
    answers: Dict[str, str] = Field(..., description="Dictionary of question-answer pairs provided by the user.")


class QuestionsResponse(BaseModel):
    questions: List[str] = Field(..., description="List of questions to be presented to the user.")

class GeneratedSkillsResponse(BaseModel):
     hard_skills: List[str] = Field(..., description="Generated list of hard skills.")

class UpdatedSkillsResponse(BaseModel):
     updated_hard_skills: str = Field(..., description="The updated hard skills text.")


class LabelValueItem(BaseModel):
    """Represents a single label-value pair returned by the AI service."""
    label: str = Field(..., description="The extracted label or category name.")
    value: str = Field(..., description="The extracted value, can be string, list, etc.")


class UpdateRequest(BaseModel):
    """Request body for updating resume data."""
    current_data: List[LabelValueItem] = Field(..., description="The current structured data as a list of label-value pairs.")
    new_info: str = Field(..., description="New information or instructions from the user.")
