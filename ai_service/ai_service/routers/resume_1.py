# routers/resume.py

# --- Annotation [routers/resume.py: 1] ---
# Import FastAPI components: APIRouter for organizing routes, Body for request body handling,
# HTTPException for returning standard HTTP errors, status for HTTP status codes.
from fastapi import APIRouter, Body, HTTPException, status, Response
from typing import List, Dict, Any # Added for type hinting hardcoded responses

# --- Annotation [routers/resume.py: 2] ---
# Import the NeuralService class that handles the core logic (LLM calls).
# --- HARDCODED: NeuralService functionality is bypassed in modified endpoints ---
from ai_service.services.neural_1 import NeuralService
#from ai_service.services import pdf_generator
# --- HARDCODED: PDFGenerator functionality is bypassed in modified endpoint ---
from ai_service.services.pdf_generator import PDFResumeGenerator
from ai_service.services.pdf_generator import create_resume_pdf

# --- Annotation [routers/resume.py: 3] ---
# Import the Pydantic schemas for request/response validation and serialization.
from ai_service.schemas.resume_1 import (
    UserAnswers,
    UpdateRequest,
    QuestionsResponse,         # Schema for returning lists of questions
    GeneratedSkillsResponse,   # Schema for returning final skills list (Original, not used for hardcoded /generate)
    UpdatedSkillsResponse,      # Schema for returning updated skills text (Original, not used for hardcoded /regenerate)
    ResumePdfRequest
)

# --- Annotation [routers/resume.py: 4] ---
# Import the application settings instance.
from ai_service.config import settings

# --- Annotation [routers/resume.py: 5] ---
# Create an APIRouter instance. Routes defined with this router
# will be included in the main FastAPI application.
# 'tags' helps group endpoints in the API documentation.
router = APIRouter(tags=["Resume Generation (Hardcoded)"]) # Renamed tag for clarity

# --- Annotation [routers/resume.py: 6] ---
# Create a single instance of the NeuralService.
# Pass the application settings to its constructor.
# This instance will be reused across requests handled by this router.
# --- HARDCODED: neural_service object created but not used by modified endpoints ---
neural_service = NeuralService(settings)

# --- Annotation [routers/resume.py: 7] ---
# Define the endpoint to get the initial set of questions (Stage 1).
# Uses GET method as it retrieves data without side effects.
# 'response_model' specifies the schema for the response, ensuring validation
# and adding it to the OpenAPI documentation.
@router.get("/api/v001/resume/basic/question", response_model=QuestionsResponse)
async def get_base_questions():
    """
    Retrieves the initial list of base questions for the resume generation process (Stage 1).
    Requires authentication (JWT).
    """
    # --- Annotation [routers/resume.py: 8] ---
    # Return the list of base questions directly from the settings.
    # FastAPI automatically converts the dictionary to a JSON response
    # matching the QuestionsResponse schema.
    return {"questions": settings.BASE_QUESTIONS}

# --- Annotation [routers/resume.py: 9] ---
# Define the endpoint to generate follow-up questions (Stage 2).
# Uses POST method as it requires data (answers) to perform an action.
# Takes 'UserAnswers' schema in the request body.
# Returns 'QuestionsResponse' schema.
# --- !!! HARDCODED RESPONSE !!! ---
@router.post("/api/v001/resume/question/get", response_model=QuestionsResponse)
# --- Annotation [routers/resume.py: 10] ---
# Mark the function as 'async' since it will call the async 'generate_follow_up_questions' method.
# 'user_answers: UserAnswers = Body(...)' indicates the request body should match
# the UserAnswers schema and is required.
async def get_next_questions(user_answers: UserAnswers = Body(...)):
    """
    [HARDCODED] Returns a fixed list of follow-up questions, regardless of input.
    Original logic generated questions based on user's answers (Stage 1 -> Stage 2).
    Requires authentication (JWT).
    """
    # --- Annotation [routers/resume.py: 11] ---
    # Basic input validation: ensure answers are provided.
    if not user_answers.answers:
         # --- Annotation [routers/resume.py: 12] ---
         # Raise HTTPException for client errors (4xx).
         # Provides a standard way to return errors with status code and detail message.
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty when requesting follow-up questions.",
        )

    # --- HARDCODED RESPONSE ---
    print(f"Received answers for /question/get (ignored): {user_answers.answers}")
    hardcoded_questions = [
        "Can you elaborate on the specific microservices you designed?",
        "Which AWS services did you utilize most frequently?",
        "Describe a challenging technical problem you solved related to database performance."
    ]
    return {"questions": hardcoded_questions}

    # --- Original Logic (Commented Out) ---
    # try:
    #     # --- Annotation [routers/resume.py: 13] ---
    #     # Call the service method to generate questions. Use 'await' because it's an async method.
    #     follow_up_questions = await neural_service.generate_follow_up_questions(user_answers.answers)
    #     # --- Annotation [routers/resume.py: 14] ---
    #     # Return the generated questions in the format expected by QuestionsResponse.
    #     return {"questions": follow_up_questions}
    # # --- Annotation [routers/resume.py: 15] ---
    # # Catch any exceptions that might occur within the service call
    # # (e.g., LLM API errors, parsing errors).
    # except Exception as e:
    #     # --- Annotation [routers/resume.py: 16] ---
    #     # Log the error server-side for debugging.
    #     print(f"Error in /next-questions endpoint: {e}")
    #     # --- Annotation [routers/resume.py: 17] ---
    #     # Raise an HTTPException for server-side errors (5xx).
    #     # Avoid exposing detailed internal error messages to the client in production.
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Failed to generate follow-up questions. Please try again later.",
    #         # detail=str(e) # Optionally include specific error in development/debug mode
    #     )
    # --- End Original Logic ---


# --- Annotation [routers/resume.py: 18] ---
# Define the endpoint for the final generation step.
# Uses POST, takes all answers combined by the client ('UserAnswers').
# --- !!! HARDCODED RESPONSE !!! ---
# NOTE: Removed `response_model` as the hardcoded structure differs from GeneratedSkillsResponse
@router.post("/api/v001/resume/label/generate") #, response_model=GeneratedSkillsResponse)
async def generate_resume_final(user_answers: UserAnswers = Body(...)) -> List[Dict[str, str]]: # Type hint for clarity
    """
    [HARDCODED] Returns a fixed list of resume labels/values, regardless of input answers.
    Original logic generated 'hard_skills' based on ALL provided answers.
    Requires authentication (JWT).
    """
    # --- Annotation [routers/resume.py: 19] ---
    # Validate that answers are provided for the final step.
    if not user_answers.answers:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty for final resume generation.",
        )

    # --- HARDCODED RESPONSE ---
    print(f"Received answers for /label/generate (ignored): {user_answers.answers}")
    hardcoded_result = [
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
    return hardcoded_result

    # --- Original Logic (Commented Out) ---
    # try:
    #     # --- Annotation [routers/resume.py: 20] ---
    #     # Call the service method to process all answers and extract skills. Use 'await'.
    #     result = await neural_service.process_answers(user_answers.answers)
    #     # --- Annotation [routers/resume.py: 21] ---
    #     # Return the result matching the GeneratedSkillsResponse schema.
    #     # The service method already returns a dict like {"hard_skills": [...]}.
    #     return result
    # except Exception as e:
    #     # --- Annotation [routers/resume.py: 22] ---
    #     # Log and handle potential errors during final generation.
    #     print(f"Error in /generate endpoint: {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Failed to generate resume skills. Please try again later.",
    #         # detail=str(e)
    #     )
    # --- End Original Logic ---


# --- Annotation [routers/resume.py: 23] ---
# Define the endpoint to update an existing section.
# Uses POST, takes 'UpdateRequest' schema in the body.
# --- !!! HARDCODED RESPONSE !!! ---
# NOTE: Removed `response_model` as the hardcoded structure differs from UpdatedSkillsResponse
@router.post("/api/v001/resume/label/regenerate") #, response_model=UpdatedSkillsResponse)
async def update_resume_section(update_req: UpdateRequest = Body(...)) -> List[Dict[str, str]]: # Type hint for clarity
    """
    [HARDCODED] Returns a fixed list of resume labels/values, regardless of input update request.
    Original logic updated a section (e.g., hard skills) using current_text and new_info.
    Requires authentication (JWT).
    """

    # --- HARDCODED RESPONSE ---
    # Note: The input `update_req` (containing current_text, new_info) is ignored.
    # The example request in the prompt ({'wish': ..., 'user_edits': ...})
    # does not match the original UpdateRequest schema. This hardcoded version
    # does not use the input data at all.
    print(f"Received update request for /label/regenerate (ignored): {update_req}")
    hardcoded_result = [
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
    return hardcoded_result

    # --- Original Logic (Commented Out) ---
    # try:
    #     # --- Annotation [routers/resume.py: 24] ---
    #     # Call the service method to perform the update. Use 'await'.
    #     result = await neural_service.update_resume(
    #         update_req.current_text,
    #         update_req.new_info
    #     )
    #     # --- Annotation [routers/resume.py: 25] ---
    #     # Return the updated text matching the UpdatedSkillsResponse schema.
    #     # The service method returns a dict like {"updated_hard_skills": "..."}.
    #     return result
    # except Exception as e:
    #     # --- Annotation [routers/resume.py: 26] ---
    #     # Log and handle potential errors during the update process.
    #     print(f"Error in /update endpoint: {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Failed to update resume section. Please try again later.",
    #         # detail=str(e)
    #     )
    # --- End Original Logic ---


# --- !!! HARDCODED RESPONSE !!! ---
@router.post("/api/v001/resume/pdf/generate")
async def generate_resume_pdf(request_data: ResumePdfRequest = Body(...)):
    """
    Generates a PDF resume summary based on ALL provided answers.
    Combines skill generation with PDF creation. Requires authentication.

    Returns:
        Response: A PDF file download.
    """
    # --- Annotation [routers/resume.py: 28] ---
    # Validate input answers.
    if not request_data.answers:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers cannot be empty for PDF generation.",
        )

    try:
        # --- Annotation [routers/resume.py: 29] ---
        # Step 1: Generate the structured skills list using the existing AI service.
        # This reuses the core logic of the '/generate' endpoint.
        user_answers = request_data.answers
        generated_skills = request_data.generated_skills

        # --- Annotation [routers/resume.py: 30] ---
        # Step 2: Call the PDF generator function with the original answers and the generated skills.
        pdf_bytes = create_resume_pdf(user_answers, generated_skills)
        pdf_bytes = bytes(pdf_bytes)

        # --- Annotation [routers/resume.py: 31] ---
        # Step 3: Create and return the FastAPI Response object.
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                # --- Annotation [routers/resume.py: 32] ---
                # Suggest a filename for the download.
                "Content-Disposition": "attachment; filename=resume_summary.pdf"
            }
        )

    except HTTPException as http_exc:
        # --- Annotation [routers/resume.py: 33] ---
        # Re-raise HTTPExceptions that might occur during skill generation.
        raise http_exc
    except Exception as e:
        # --- Annotation [routers/resume.py: 34] ---
        # Handle potential errors during skill generation or PDF creation.
        print(f"Error in /generate-pdf endpoint: {e}")
        # Add more specific logging if needed (e.g., traceback)
        # import traceback
        # traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate resume PDF. Please try again later.",
        )
