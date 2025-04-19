# services/neural.py

# --- Annotation [services/neural.py: 1] ---
# Use httpx for making async HTTP calls to the LLM API.
import httpx
import json
import re
# --- Annotation [services/neural.py: 2] ---
# Import settings and typing helpers.
from ai_service.config import Settings
from typing import Dict, List # Explicit type hints

class NeuralService:
    # --- Annotation [services/neural.py: 3] ---
    # Constructor (__init__) to initialize the service instance.
    # It takes the application settings as an argument.
    def __init__(self, settings: Settings):
        self.settings = settings
        # --- Annotation [services/neural.py: 4] ---
        # Prepare headers required by the OpenRouter API (or other LLM API).
        # Note: Content-Type is often added automatically by httpx when using json=
        self.headers = {
            "Authorization": f"Bearer {self.settings.API_KEY}",
            # "Content-Type": "application/json" # Usually not needed with httpx json=
        }
        # --- Annotation [services/neural.py: 5] ---
        # Add checks during initialization to warn if critical settings seem missing.


        if not self.settings.API_KEY or self.settings.API_KEY == "some-key":
            print("Warning: OPENROUTER_API_KEY not set or using default in config.")
        if not self.settings.AUTH_SERVICE_URL or "localhost" in self.settings.AUTH_SERVICE_URL:
             print(f"Warning: AUTH_SERVICE_URL is not set or using default/localhost value ({self.settings.AUTH_SERVICE_URL}). Ensure it's correct for your environment (e.g., Docker Compose service name).")

    # --- Annotation [services/neural.py: 6] ---
    # Internal helper method to call the LLM API. Made async to use httpx.
    # Takes user content and the specific system prompt to use.
    async def _call_api(self, user_content: str, system_prompt: str) -> str:
        """Sends request to the LLM API and returns the response content."""
        # --- Annotation [services/neural.py: 7] ---
        # Define the payload for the LLM API request according to its documentation.
        data = {

            "model": "deepseek/deepseek-r1-zero:free", # Consider model choice based on task (coder good for JSON/instructions)

            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.4, # Adjust temperature (0.3-0.5 often good for structured output)
            "max_tokens": 500,
            # --- Annotation [services/neural.py: 8] ---
            # Request JSON output format if the model/API supports it.
            # This increases the chance of getting well-formatted JSON, especially for questions.
            # Check OpenRouter/model docs if "json_object" is the correct value.
            # Some APIs might use "response_format": { "type": "json" } etc.
            "response_format": {"type": "json_object"}
        }

        # --- Annotation [services/neural.py: 9] ---
        # Use httpx.AsyncClient for the async request.
        async with httpx.AsyncClient() as client:
            try:
                # --- Annotation [services/neural.py: 10] ---
                # Make the asynchronous POST request to the LLM API URL.
                # Pass the prepared headers and JSON payload. Set a timeout.
                response = await client.post(
                    self.settings.API_URL,
                    json=data,
                    headers=self.headers,
                    timeout=45.0 # Increased timeout for potentially long LLM responses
                )

                # --- Annotation [services/neural.py: 11] ---
                # Raise an exception for bad status codes (4xx or 5xx).
                # This provides immediate feedback on API errors.
                response.raise_for_status()

                # --- Annotation [services/neural.py: 12] ---
                # Parse the JSON response from the API.
                response_data = response.json()
                # print(f"LLM Raw Response: {response_data}") # Debugging line

                # --- Annotation [services/neural.py: 13] ---
                # Safely extract the content from the expected response structure.
                # Check if 'choices' exists and is not empty.
                if 'choices' in response_data and len(response_data['choices']) > 0:
                     # Get the first choice's message object.
                     message = response_data['choices'][0].get('message', {})
                     # Get the content from the message object.
                     content = message.get('content')
                     if content:
                         # Return the extracted text content.
                         return content
                     else:
                          # Raise error if content is missing within the message.
                          raise Exception("LLM API Error: No 'content' found in the response message.")
                else:
                    # Raise error if the 'choices' structure is missing or empty.
                    raise Exception("LLM API Error: Invalid response structure - 'choices' not found or empty.")

            # --- Annotation [services/neural.py: 14] ---
            # Catch specific httpx network errors.
            except httpx.RequestError as e:
                print(f"LLM API Request Error: {e}")
                # Re-raise as a generic Exception or a custom one for the router to catch.
                raise Exception(f"Could not connect to LLM API: {e}")
            # --- Annotation [services/neural.py: 15] ---
            # Catch HTTP status errors (4xx, 5xx) raised by raise_for_status().
            except httpx.HTTPStatusError as e:
                 print(f"LLM API HTTP Error: {e.response.status_code} - {e.response.text}")
                 raise Exception(f"LLM API returned an error: {e.response.status_code}")
            # --- Annotation [services/neural.py: 16] ---
            # Catch JSON decoding errors if the API response isn't valid JSON.
            except json.JSONDecodeError as e:
                print(f"LLM API JSON Decode Error: {e}")
                raise Exception(f"Failed to parse LLM API response as JSON.")
            # --- Annotation [services/neural.py: 17] ---
            # Catch any other unexpected errors during the API call or processing.
            except Exception as e:
                print(f"LLM API Processing Error: {e}")
                # Re-raise the caught exception.
                raise e

    # --- Annotation [services/neural.py: 18] ---
    # Method to process ALL answers (combined from stages) to generate the final skills list.
    # Marked async because it calls the async _call_api method.
    async def process_answers(self, answers: Dict[str, str]) -> Dict[str, List[str]]:
        """Generates the final 'hard_skills' list based on all answers."""
        # --- Annotation [services/neural.py: 19] ---
        # Combine all questions and answers into a single text block for the LLM.
        user_text = "\n".join(f"Q: {k}\nA: {v}" for k, v in answers.items())
        user_text += '\n\n---\nИзвлеки навыки из ответов выше. Предоставь их в формате JSON-объекта: {"hard_skills": "C/C++, HTML, CSS, REST API", "experience": "Я работал в X компании на позиции... Я сопровождал весь проект от создания до выката в прод...", "technologies": "..."}'

        # --- Annotation [services/neural.py: 20] ---
        # Call the LLM API using the specific system prompt for SKILL EXTRACTION.
        nn_response_text = await self._call_api(user_text, self.settings.SYSTEM_PROMPT)

        # --- Annotation [services/neural.py: 21] ---
        # Basic parsing of the LLM response. Assumes the LLM follows the prompt
        # and returns a list-like structure, potentially with categories.
        # More robust parsing might be needed depending on LLM consistency.
        skills_list = [line.strip() for line in nn_response_text.split('\n') if line.strip() and not line.strip().endswith(':')]
        # This simple split might need refinement based on actual LLM output format.

        # --- Annotation [services/neural.py: 22] ---
        # Return the result in the desired dictionary format.
        return {
            # "experience_summary": "Placeholder for experience summary.", # Add if needed later
            "hard_skills": skills_list # Return the parsed list of skills
        }

    # --- Annotation [services/neural.py: 23] ---
    # Method to generate follow-up questions based on Stage 1 answers.
    # Marked async because it calls the async _call_api method.
    async def generate_follow_up_questions(self, answers: Dict[str, str]) -> List[str]:
        """Generates follow-up questions based on previous answers using the LLM."""
        user_text = "Предыдущие ответы пользователя:\n" + "\n".join(f"- {k}: {v}" for k, v in answers.items())
        # Updated instruction consistent with the new prompt
        user_text += '\n\n---\nСгенерируй 5-7 уточняющих вопросов на основе этих ответов в формате JSON-объекта {"questions": ["вопрос1", "вопрос2", ...]}'

        print("Sending request to LLM for follow-up questions...")
        raw_response = await self._call_api(user_text, self.settings.FOLLOW_UP_QUESTIONS_PROMPT)
        print(f"LLM Raw Response for questions: {raw_response}") # Keep logging raw response

        #--- Annotation [services/neural.py: 26] ---
        # Attempt to parse the LLM response, expecting a JSON array of strings.
        try:
            # --- Annotation [services/neural.py: 27] ---
            # Handle cases where the LLM might wrap the JSON in markdown code blocks
            # AND remove potential trailing artifacts like \boxed{...}
            processed_response = raw_response.strip()
            if '\\boxed' in processed_response:
                index = processed_response.find('\\boxed')
                processed_response = processed_response[index + len('\\boxed'):]
            # Remove markdown blocks first
            if processed_response.startswith("```json"):
                processed_response = processed_response[7:-3].strip()
            elif processed_response.startswith("```"):
                 processed_response = processed_response[3:-3].strip()

            # --- NEW: Find the end of the actual JSON data ---
            # Find the last occurrence of '}' or ']' which likely marks the end
            # of the primary JSON object or array returned by the LLM.
            last_brace = processed_response.rfind('}')
            last_bracket = processed_response.rfind(']')
            end_json_pos = max(last_brace, last_bracket)

            if end_json_pos != -1:
                # Truncate the string just after the found brace/bracket
                processed_response = processed_response[:end_json_pos + 1]
            else:
                # If no '}' or ']' is found, the response is likely not valid JSON anyway
                # Let json.loads handle the error below.
                print("Warning: No closing brace or bracket found in LLM response for questions.")

            # Log the cleaned response right before parsing
            print(f"Cleaned response before parsing was:\n{processed_response}")

            # --- Annotation [services/neural.py: 28] ---
            # Parse the cleaned string as JSON.
            questions_data = json.loads(processed_response)

            # --- Annotation [services/neural.py: 29] ---
            # Validate the structure: should be a list of strings OR a dict containing a list.
            if isinstance(questions_data, list) and all(isinstance(item, str) for item in questions_data):
                return questions_data
            # --- Annotation [services/neural.py: 30] ---
            # Handle alternative structure sometimes returned: {"questions": [...]}.
            elif isinstance(questions_data, dict) and "questions" in questions_data and isinstance(questions_data["questions"], list):
                 if all(isinstance(item, str) for item in questions_data["questions"]):
                     return questions_data["questions"]
                 else:
                     raise ValueError("LLM returned a 'questions' list, but it contains non-string items.")
            else:
                 # --- Annotation [services/neural.py: 31] ---
                 print(f"Warning: LLM returned unexpected JSON structure for questions: {questions_data}")
                 raise ValueError("LLM did not return a valid JSON list/object of strings for questions.")

        # --- Annotation [services/neural.py: 32] ---
        # Catch JSON decoding errors.
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for questions: {e}")
            # Log the problematic string *again* in case of error
            print(f"LLM Raw response was:\n{raw_response}")
            print(f"String attempted for parsing was:\n{processed_response}")
            raise Exception(f"Failed to parse questions from LLM response (Invalid JSON).")

    # --- Annotation [services/neural.py: 35] ---
    # Method to update resume text (currently focused on skills).
    # Marked async because it calls the async _call_api method.
    async def update_resume(self, current_text: str, new_info: str) -> Dict[str, str]:
        """Updates the resume section based on new info (uses skill extraction prompt)."""
        # --- Annotation [services/neural.py: 36] ---
        # Combine existing text and new info to provide full context for update.
        # The prompt should ideally guide the LLM on how to integrate the new info.
        user_content = f"Текущий раздел:\n{current_text}\n\nДополнительная информация от пользователя:\n{new_info}\n\n---\nПерепиши и обнови раздел, интегрировав новую информацию и сохранив структуру и правила изначального задания (извлечение навыков)."

        # --- Annotation [services/neural.py: 37] ---
        # Call the LLM API using the main SKILL EXTRACTION prompt, but with context about updating.
        # Alternatively, you might create a dedicated UPDATE_PROMPT if needed.
        nn_response = await self._call_api(user_content, self.settings.SYSTEM_PROMPT)
        # --- Annotation [services/neural.py: 38] ---
        # Return the updated text. Parsing might be needed here too if structure is expected.
        return {"updated_hard_skills": nn_response}
