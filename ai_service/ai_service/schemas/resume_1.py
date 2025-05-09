# schemas/resume.py

# --- Annotation [schemas/resume.py: 1] ---
# Import BaseModel from Pydantic for data validation and serialization.
# Import typing hints for clarity and type checking.
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

# --- Annotation [schemas/resume.py: 2] ---
# Schema for receiving user answers.
# Used as input for '/next-questions' and '/generate' endpoints.
class UserAnswers(BaseModel):
    # --- Annotation [schemas/resume.py: 3] ---
    # A dictionary where keys are the questions (str)
    # and values are the user's answers (str).
    answers: Dict[str, str] = Field(..., description="Dictionary of question-answer pairs provided by the user.")
    # Example: {"question1": "answer1", "question2": "answer2"}


# --- Annotation [schemas/resume.py: 7] ---
# Schema for returning a list of questions to the user.
# Used as the response model for '/questions' and '/next-questions'.
class QuestionsResponse(BaseModel):
    # --- Annotation [schemas/resume.py: 8] ---
    # A list containing the questions (strings).
    questions: List[str] = Field(..., description="List of questions to be presented to the user.")
    # Example: ["Question 1?", "Question 2?"]

# --- Annotation [schemas/resume.py: 9] ---
# Schema for returning the final generated hard skills.
# Used as the response model for '/generate'.
class GeneratedSkillsResponse(BaseModel):
     # --- Annotation [schemas/resume.py: 10] ---
     # A list containing the extracted and formatted hard skills (strings).
     hard_skills: List[str] = Field(..., description="Generated list of hard skills.")
     # Example: ["Python", "FastAPI", "Docker"]

# --- Annotation [schemas/resume.py: 11] ---
# Schema for returning the updated hard skills text.
# Used as the response model for '/update'.
class UpdatedSkillsResponse(BaseModel):
     # --- Annotation [schemas/resume.py: 12] ---
     # The full text of the updated hard skills section (string).
     updated_hard_skills: str = Field(..., description="The updated hard skills text.")


class LabelValueItem(BaseModel):
    """Represents a single label-value pair returned by the AI service."""
    label: str = Field(..., description="The extracted label or category name.")
    value: str = Field(..., description="The extracted value, can be string, list, etc.")


# --- Annotation [schemas/resume.py: 4] ---
# Schema for the request to update an existing resume section.
# Used as input for the '/update' endpoint.
class UpdateRequest(BaseModel):
    """Request body for updating resume data."""
    # NeuralService.update_resume expects List[Dict[str, Any]] for current_data
    current_data: List[LabelValueItem] = Field(..., description="The current structured data as a list of label-value pairs.")
    new_info: str = Field(..., description="New information or instructions from the user.")
