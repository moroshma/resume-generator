# services/neural.py

import httpx
import json
# import re # Keep if needed, but json_object format helps
from ai_service.config import Settings # Assuming Settings now has HF_ROUTER_API_KEY etc.
from typing import Dict, List, Any

class NeuralService:
    def __init__(self, settings: Settings):
        self.settings = settings
        # --- Annotation [HF Router Change 1]: Use HF Router settings ---
        # Ensure your Settings class has these attributes defined
        # e.g., HF_ROUTER_API_KEY = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        #       HF_ROUTER_API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
        #       HF_ROUTER_MODEL_ID = "deepseek/deepseek-v3-0324" # Or your chosen model
        self.api_key = self.settings.API_KEY
        self.api_url = self.settings.API_URL
        self.model_id = self.settings.MODEL_ID

        # --- Annotation [HF Router Change 2]: Set up standard OpenAI-compatible headers ---
        # This header format is correct for the HF Router endpoint
        if not self.api_key or not self.api_key.startswith("hf_"): # Check for missing or invalid-looking key
             print("Warning: HF_ROUTER_API_KEY not set or doesn't look like a valid Hugging Face token in config.")
             # Decide if you want to proceed without auth or raise an error
             self.headers = {
                 "Content-Type": "application/json",
             }
             # Consider raising ValueError("HF_ROUTER_API_KEY is missing or invalid.")
        else:
             self.headers = {
                 "Authorization": f"Bearer {self.api_key}",
                 "Content-Type": "application/json",
             }

        # --- Annotation [HF Router Change 3]: Update initialization checks/warnings ---
        if not self.api_url:
             print("Warning: HF_ROUTER_API_URL is not set in config.")
             # Consider raising ValueError("HF_ROUTER_API_URL is missing.")
        if not self.model_id:
             print("Warning: HF_ROUTER_MODEL_ID is not set in config.")
             # Consider raising ValueError("HF_ROUTER_MODEL_ID is missing.")

        # Keep the AUTH_SERVICE_URL check if it's still relevant to your architecture
        if not self.settings.AUTH_SERVICE_URL or "localhost" in self.settings.AUTH_SERVICE_URL:
             print(f"Warning: AUTH_SERVICE_URL is not set or using default/localhost value ({self.settings.AUTH_SERVICE_URL}). Ensure it's correct for your environment.")


    async def _call_api(self, user_content: str, system_prompt: str, request_json_output: bool = False) -> str:
        """Sends request to the Hugging Face Router API (OpenAI format) and returns the response content."""

        # --- Annotation [HF Router Change 4]: Construct OpenAI-compatible payload ---
        # This structure is identical to what the HF Router endpoint expects. No changes needed here.
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_content})

        print('\n-------\n',self.api_key,'\n-------\n')

        data: Dict[str, Any] = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.4, # Adjust as needed
            "max_tokens": 4096, # Adjust based on model/needs (check model limits)
            # "top_p": 0.9, # Optional OpenAI parameter
            # "stream": False, # Set to True if you want streaming responses
        }

        # --- Annotation [HF Router Change 5]: Request JSON output if needed (OpenAI format) ---
        # This standard OpenAI parameter should work if the underlying model/endpoint supports it.
        if request_json_output:
             data["response_format"] = {"type": "json_object"}
             # Crucial: Also keep instructions in the *prompt* itself to return JSON, as model adherence varies.

        async with httpx.AsyncClient() as client:

            try:
                # --- Annotation [HF Router Change 6]: Make POST request to HF Router URL ---
                print(f"Sending request to Hugging Face Router API: {self.api_url}")
                # print(f"Payload: {json.dumps(data, indent=2)}") # Debugging: careful logging keys
                # print(f"Headers: {self.headers}") # Debugging

                response = await client.post(
                    self.api_url,
                    json=data,
                    headers=self.headers, # Pass headers with Auth
                    timeout=90.0 # Adjust timeout - HF Router might sometimes be slower than specialized providers
                )

                response.raise_for_status() # Check for 4xx/5xx errors

                response_data = response.json()
                # print(f"HF Router Raw Response: {json.dumps(response_data, indent=2)}") # Debugging

                # --- Annotation [HF Router Change 7]: Parse OpenAI-compatible response structure ---
                # This logic remains the same as the response format is standard OpenAI.
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    finish_reason = choice.get("finish_reason")

                    # Log finish reason for debugging potential issues (e.g., length, content filter)
                    if finish_reason != "stop" and finish_reason != "eos": # 'eos' is common end-of-sequence token
                         print(f"Warning: HF Router generation finished unexpectedly. Reason: {finish_reason}")
                         # Consider how to handle non-stop finishes (e.g., length limit, content filter)

                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        if content:
                             # If JSON was requested, this 'content' should be a valid JSON string
                             return content.strip() # Strip any leading/trailing whitespace
                        else:
                            # Handle potential empty content string if finish_reason wasn't 'stop'
                            if finish_reason == "length":
                                print("Warning: Generation stopped due to length limit, content might be incomplete.")
                                return content # Return potentially incomplete content
                            elif finish_reason == "content_filter":
                                raise Exception("HF Router API Error: Content filtered.")
                            else:
                                raise Exception(f"HF Router API Error: Empty 'content' in the response message. Finish reason: {finish_reason}")
                    else:
                        raise Exception("HF Router API Error: Invalid response structure - 'message' or 'content' missing in choice.")
                # --- Annotation [HF Router Change 8]: Handle API specific errors (OpenAI format) ---
                elif "error" in response_data:
                    error_info = response_data["error"]
                    err_msg = error_info.get('message', 'Unknown error')
                    err_type = error_info.get('type', 'N/A')
                    err_code = error_info.get('code', 'N/A')
                    raise Exception(f"HF Router API Error: Type: {err_type}, Code: {err_code}, Message: {err_msg}")
                else:
                    # If no choices and no explicit error, the response is unexpected
                    raise Exception("HF Router API Error: Invalid response structure - 'choices' not found or empty, and no error field.")

            except httpx.RequestError as e:
                print(f"HF Router API Request Error: {e}")
                url_object = httpx.URL(self.api_url)
                raise Exception(f"Could not connect to HF Router API at {url_object.host}: {e}") from e
            except httpx.HTTPStatusError as e:
                 print(f"HF Router API HTTP Error: {e.response.status_code} - {e.response.text}")
                 error_details = "No details provided in response body."
                 try:
                     error_data = e.response.json()
                     if "error" in error_data and "message" in error_data["error"]:
                         error_details = error_data["error"]["message"]
                     elif "detail" in error_data: # Some HF errors might use 'detail'
                         error_details = error_data["detail"]
                     else:
                         error_details = e.response.text
                 except json.JSONDecodeError:
                     error_details = e.response.text
                 raise Exception(f"HF Router API returned an error: {e.response.status_code}. Details: {error_details}") from e
            except json.JSONDecodeError as e:
                 print(f"HF Router API JSON Decode Error: {e}")
                 raw_text = "Could not retrieve raw text"
                 if 'response' in locals() and hasattr(response, 'text'):
                     raw_text = response.text
                 raise Exception(f"Failed to parse HF Router API response as JSON. Raw text: {raw_text}") from e
            except Exception as e:
                 # Catch the specific exceptions raised above or any other unexpected ones
                 print(f"HF Router API Processing Error: {e}")
                 raise e # Re-raise the caught exception

    async def process_answers(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """Generates structured skills/experience data based on answers using HF Router."""
        user_text_parts = [f"Q: {k}\nA: {v}" for k, v in answers.items()]
        user_text = "\n".join(user_text_parts)

        # --- Annotation [HF Router Change 9]: Ensure prompt clearly requests JSON format ---
        # This prompt structure remains valid.
        user_text += '\n\n---\nИзвлеки из приведенных выше ответов на вопросы релевантную информацию о кандидате и верни ее СТРОГО в формате JSON со следующими ключами: {"hard_skills": ["навык1", "навык2", ...], "experience_summary": "Краткое описание опыта...", "technologies": ["технология1", "технология2", ...]}. В ответе должен быть ТОЛЬКО JSON-объект и ничего больше.'

        # --- Annotation [HF Router Change 10]: Call API requesting JSON output ---
        # Set request_json_output=True
        nn_response_text = await self._call_api(
            user_text,
            self.settings.SYSTEM_PROMPT, # Use the appropriate system prompt from settings
            request_json_output=True
        )
        print(f"HF Router Raw JSON String for Skills: {nn_response_text}") # Log raw response

        try:
            # --- Annotation [HF Router Change 11]: Parse the JSON string directly ---
            # Keep the cleaning logic as models might still occasionally wrap output.
            cleaned_response = nn_response_text.strip()
            if cleaned_response.startswith("```json"):
                 cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith("```"):
                 cleaned_response = cleaned_response[3:-3].strip()

            # Handle potential empty string before parsing
            if not cleaned_response:
                raise json.JSONDecodeError("Empty string received from API", cleaned_response, 0)

            parsed_data = json.loads(cleaned_response)

            # --- Annotation [HF Router Change 12]: Validate and extract data (same logic) ---
            # This logic remains the same.
            hard_skills = parsed_data.get("hard_skills", [])
            experience = parsed_data.get("experience_summary", "")
            technologies = parsed_data.get("technologies", [])

            if not isinstance(hard_skills, list):
                print(f"Warning: 'hard_skills' is not a list in LLM response: {hard_skills}")
                hard_skills = []
            if not isinstance(technologies, list):
                 print(f"Warning: 'technologies' is not a list in LLM response: {technologies}")
                 technologies = []

            safe_hard_skills = [str(skill) for skill in hard_skills if isinstance(skill, (str, int, float))]
            safe_technologies = [str(tech) for tech in technologies if isinstance(tech, (str, int, float))]

            return {
                "hard_skills": safe_hard_skills,
                "experience_summary": str(experience),
                "technologies": safe_technologies
            }

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for skills: {e}")
            print(f"LLM Raw response string was:\n{nn_response_text}")
            # Only print cleaned_response if it was assigned
            if 'cleaned_response' in locals():
                print(f"Cleaned string attempted for parsing was:\n{cleaned_response}")
            raise Exception(f"Failed to parse skills from LLM response (Invalid JSON).") from e
        except Exception as e:
             print(f"Error processing skills response: {e}")
             raise e


    async def generate_follow_up_questions(self, answers: Dict[str, str]) -> List[str]:
        """Generates follow-up questions based on previous answers using HF Router."""
        user_text = "Предыдущие ответы пользователя:\n" + "\n".join(f"- {k}: {v}" for k, v in answers.items())
        # --- Annotation [HF Router Change 13]: Update prompt for HF Router, ensure JSON request ---
        # Prompt structure remains valid.
        user_text += '\n\n---\nНа основе этих ответов, сгенерируй 5-7 УТОЧНЯЮЩИХ вопросов, чтобы глубже понять опыт и навыки кандидата. Верни результат СТРОГО в формате JSON-объекта: {"questions": ["вопрос1", "вопрос2", ...]}. В ответе должен быть ТОЛЬКО JSON-объект и ничего больше.'

        print("Sending request to HF Router for follow-up questions...")
        # --- Annotation [HF Router Change 14]: Call API requesting JSON output ---
        raw_response = await self._call_api(
            user_text,
            self.settings.FOLLOW_UP_QUESTIONS_PROMPT, # Use specific prompt if defined
            request_json_output=True
        )
        print(f"HF Router Raw JSON String for questions: {raw_response}") # Log raw response

        try:
            # --- Annotation [HF Router Change 15]: Clean and parse JSON (same logic) ---
            processed_response = raw_response.strip()
            if processed_response.startswith("```json"):
                processed_response = processed_response[7:-3].strip()
            elif processed_response.startswith("```"):
                 processed_response = processed_response[3:-3].strip()

            print(f"Cleaned response before parsing questions was:\n{processed_response}")

            # Handle potential empty string before parsing
            if not processed_response:
                raise json.JSONDecodeError("Empty string received from API", processed_response, 0)

            questions_data = json.loads(processed_response)

            # Validation logic remains the same.
            if isinstance(questions_data, dict) and "questions" in questions_data and isinstance(questions_data["questions"], list):
                 questions_list = questions_data["questions"]
                 valid_questions = [str(item) for item in questions_list if isinstance(item, str)]
                 if len(valid_questions) != len(questions_list):
                      print("Warning: 'questions' list contained non-string items. They were filtered out.")
                 if not valid_questions:
                      print("Warning: 'questions' list extracted, but was empty or contained only non-strings.")
                 return valid_questions
            else:
                 if isinstance(questions_data, list) and all(isinstance(item, str) for item in questions_data):
                      print("Warning: LLM returned a list directly instead of {'questions': [...]}. Using the list.")
                      return questions_data
                 print(f"Error: HF Router returned unexpected JSON structure for questions: {questions_data}")
                 raise ValueError("HF Router did not return a valid JSON object with a 'questions' list of strings.")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for questions: {e}")
            print(f"LLM Raw response string was:\n{raw_response}")
            # Only print processed_response if it was assigned
            if 'processed_response' in locals():
                print(f"String attempted for parsing was:\n{processed_response}")
            raise Exception(f"Failed to parse questions from HF Router response (Invalid JSON).") from e
        except Exception as e:
             print(f"Error processing follow-up questions response: {e}")
             raise e

    async def update_resume(self, current_text: str, new_info: str) -> Dict[str, Any]: # Возвращаем Any, т.к. структура как у process_answers
        """Analyzes the combined text and re-extracts structured data."""
        # Объединяем тексты для анализа LLM
        combined_text = f"Текущий контекст резюме:\n{current_text}\n\nДополнительные инструкции/информация от пользователя:\n{new_info}"

        # Используем тот же промпт, что и для process_answers, чтобы получить ту же структуру
        user_prompt_instruction = '\n\n---\nПроанализируй весь приведенный выше текст (контекст + инструкции) и верни обновленную информацию о кандидате СТРОГО в формате JSON со следующими ключами: {"hard_skills": ["навык1", ...], "experience_summary": "...", "technologies": [...]}. В ответе должен быть ТОЛЬКО JSON-объект.'
        full_user_content = combined_text + user_prompt_instruction

        # Запрашиваем JSON и используем SYSTEM_PROMPT
        nn_response_text = await self._call_api(
            full_user_content,
            self.settings.SYSTEM_PROMPT, # Используем промпт для извлечения
            request_json_output=True # Обязательно требуем JSON
        )
        print(f"Raw JSON String for REGENERATED Skills: {nn_response_text}")

        try:
            # Парсинг и валидация - точно так же, как в process_answers
            cleaned_response = nn_response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:-3].strip()

            if not cleaned_response:
                raise json.JSONDecodeError("Empty string received from API", cleaned_response, 0)

            parsed_data = json.loads(cleaned_response)

            hard_skills = parsed_data.get("hard_skills", [])
            experience = parsed_data.get("experience_summary", "")
            technologies = parsed_data.get("technologies", [])

            # Basic validation
            if not isinstance(hard_skills, list): hard_skills = []
            if not isinstance(technologies, list): technologies = []

            safe_hard_skills = [str(skill) for skill in hard_skills if isinstance(skill, (str, int, float))]
            safe_technologies = [str(tech) for tech in technologies if isinstance(tech, (str, int, float))]

            # Возвращаем словарь в нужной структуре
            return {
                "hard_skills": safe_hard_skills,
                "experience_summary": str(experience),
                "technologies": safe_technologies
            }

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for REGENERATED skills: {e}")
            print(f"LLM Raw response string was:\n{nn_response_text}")
            raise Exception(f"Failed to parse REGENERATED skills from LLM response (Invalid JSON).") from e
        except Exception as e:
            print(f"Error processing REGENERATED skills response: {e}")
            raise e
