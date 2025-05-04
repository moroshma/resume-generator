# services/neural.py

import httpx
import json
from ai_service.config import Settings # Assuming Settings now has HF_ROUTER_API_KEY etc.
from typing import Dict, List, Any, Union # Добавили Union

class NeuralService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = self.settings.API_KEY
        self.api_url = self.settings.API_URL
        self.model_id = self.settings.MODEL_ID

        if not self.api_key or not self.api_key.startswith("hf_"):
             print("Warning: HF_ROUTER_API_KEY not set or doesn't look like a valid Hugging Face token in config.")
             self.headers = {"Content-Type": "application/json"}
        else:
             self.headers = {
                 "Authorization": f"Bearer {self.api_key}",
                 "Content-Type": "application/json",
             }

        if not self.api_url: print("Warning: HF_ROUTER_API_URL is not set in config.")
        if not self.model_id: print("Warning: HF_ROUTER_MODEL_ID is not set in config.")
        if not self.settings.AUTH_SERVICE_URL or "localhost" in self.settings.AUTH_SERVICE_URL:
             print(f"Warning: AUTH_SERVICE_URL is not set or using default/localhost value ({self.settings.AUTH_SERVICE_URL}). Ensure it's correct for your environment.")


    async def _call_api(self, user_content: str, system_prompt: str, request_json_output: bool = False) -> str:
        """Sends request to the Hugging Face Router API (OpenAI format) and returns the response content."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_content})

        # print('\n-------\n',self.api_key,'\n-------\n') # Debugging: Avoid printing keys in production logs

        data: Dict[str, Any] = {
            "model": self.model_id,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 4096,
            # "stream": False,
        }

        if request_json_output:
             data["response_format"] = {"type": "json_object"}
             # Prompt should also strongly request JSON list format

        async with httpx.AsyncClient() as client:
            try:
                # print(f"Sending request to Hugging Face Router API: {self.api_url}") # Debugging
                response = await client.post(
                    self.api_url,
                    json=data,
                    headers=self.headers,
                    timeout=90.0
                )
                response.raise_for_status()
                response_data = response.json()
                # print(f"HF Router Raw Response: {json.dumps(response_data, indent=2)}") # Debugging

                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    finish_reason = choice.get("finish_reason")
                    if finish_reason != "stop" and finish_reason != "eos":
                         print(f"Warning: HF Router generation finished unexpectedly. Reason: {finish_reason}")

                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                        if content:
                             return content.strip()
                        else:
                            if finish_reason == "length":
                                print("Warning: Generation stopped due to length limit, content might be incomplete.")
                                return content # Return potentially incomplete content
                            elif finish_reason == "content_filter":
                                raise Exception("HF Router API Error: Content filtered.")
                            else:
                                raise Exception(f"HF Router API Error: Empty 'content'. Finish reason: {finish_reason}")
                    else:
                        raise Exception("HF Router API Error: Invalid response - 'message' or 'content' missing.")
                elif "error" in response_data:
                    error_info = response_data["error"]
                    raise Exception(f"HF Router API Error: Type: {error_info.get('type','N/A')}, Code: {error_info.get('code','N/A')}, Message: {error_info.get('message', 'Unknown error')}")
                else:
                    raise Exception("HF Router API Error: Invalid response - no 'choices' or 'error'.")

            except httpx.RequestError as e:
                print(f"HF Router API Request Error: {e}")
                raise Exception(f"Could not connect to HF Router API at {self.api_url}: {e}") from e
            except httpx.HTTPStatusError as e:
                 print(f"HF Router API HTTP Error: {e.response.status_code} - {e.response.text}")
                 error_details = e.response.text
                 try: error_details = e.response.json().get("error", {}).get("message", error_details)
                 except json.JSONDecodeError: pass
                 raise Exception(f"HF Router API returned an error: {e.response.status_code}. Details: {error_details}") from e
            except json.JSONDecodeError as e:
                 print(f"HF Router API JSON Decode Error: {e}")
                 raw_text = "Could not retrieve raw text"
                 if 'response' in locals() and hasattr(response, 'text'): raw_text = response.text
                 raise Exception(f"Failed to parse HF Router API response as JSON. Raw text: {raw_text}") from e
            except Exception as e:
                 print(f"HF Router API Processing Error: {e}")
                 raise e

    def _clean_llm_json_response(self, raw_response: str) -> str:
        """Cleans potential markdown code blocks from the LLM JSON response string."""
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        elif cleaned.startswith("```"):
             cleaned = cleaned[3:]
             if cleaned.endswith("```"):
                  cleaned = cleaned[:-3]
        return cleaned.strip()

    def _parse_label_value_list(self, json_string: str, context: str = "response") -> List[Dict[str, Any]]:
        """
        Parses a JSON string expected to contain a list of {"label": ..., "value": ...} dicts.

        Args:
            json_string: The raw JSON string from the LLM.
            context: A string describing the context (e.g., "skills response", "update response") for logging.

        Returns:
            A list of dictionaries, each containing 'label' and 'value'.

        Raises:
            ValueError: If the JSON is invalid or doesn't match the expected structure.
            json.JSONDecodeError: If the string is not valid JSON.
        """
        cleaned_response = self._clean_llm_json_response(json_string)

        if not cleaned_response:
            print(f"Warning: Received empty string after cleaning LLM {context}.")
            return [] # Return empty list for empty input

        try:
            parsed_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON {context}: {e}")
            print(f"LLM Raw response string was:\n{json_string}")
            print(f"Cleaned string attempted for parsing was:\n{cleaned_response}")
            raise ValueError(f"Failed to parse LLM {context} (Invalid JSON).") from e

        # --- NEW Flexible Validation ---
        if not isinstance(parsed_data, list):
            print(f"Error: Expected LLM {context} to be a JSON list, but received type {type(parsed_data)}.")
            print(f"Received data: {parsed_data}")
            # Option: Try to find the list if it's nested? e.g., parsed_data.get("data")
            # For now, enforce strict top-level list requirement based on prompt.
            raise ValueError(f"LLM {context} did not return a JSON list as expected.")

        processed_list: List[Dict[str, Any]] = []
        for index, item in enumerate(parsed_data):
            if isinstance(item, dict) and "label" in item and "value" in item:
                label = item.get("label")
                value = item.get("value") # Value can be string, list, etc.

                # Basic type validation for label
                if not isinstance(label, str) or not label.strip():
                     print(f"Warning: Skipping item at index {index} in LLM {context} due to invalid or empty label: {label}")
                     continue

                # You might want to add validation/transformation for 'value' here if needed
                # For example, ensuring skills/technologies are lists or strings.
                # For now, we accept Any valid JSON type for flexibility.
                processed_list.append({"label": label.strip(), "value": value})
            else:
                print(f"Warning: Skipping invalid item at index {index} in LLM {context} list. Expected {{'label': ..., 'value': ...}}, got: {item}")

        if not processed_list and parsed_data: # Original list wasn't empty, but nothing valid was found
             print(f"Warning: LLM {context} was a list, but contained no valid {{'label':..., 'value':...}} items.")

        return processed_list
        # --- End NEW Flexible Validation ---


    async def process_answers(self, answers: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generates structured data as a list of label/value pairs based on answers.
        Returns a list like [{"label": "hard_skills", "value": "..."}, {"label": "experience", "value": "..."}].
        """
        user_text_parts = [f"Q: {k}\nA: {v}" for k, v in answers.items()]
        user_text = "\n".join(user_text_parts)

        # --- Ensure prompt clearly requests the List[Dict] JSON format ---
        # Using the SYSTEM_PROMPT which should be updated in config.py
        # Example user instruction part (append to user_text):
        user_text += '\n\n---\nИзвлеки из приведенных выше ответов на вопросы релевантную информацию о кандидате и верни ее СТРОГО в формате JSON-**списка** объектов: `[{"label":"название_поля","value":"значение_поля"}, {"label":"другое_поле","value":"..."}, ...]`. В ответе должен быть ТОЛЬКО этот JSON-список и ничего больше.'

        nn_response_text = await self._call_api(
            user_text,
            self.settings.SYSTEM_PROMPT, # Ensure this prompt requests the [{"label":..."value":...}] list format
            request_json_output=True
        )
        print(f"HF Router Raw JSON String for Skills: {nn_response_text}") # Log raw response

        try:
            # --- Use the new parsing helper ---
            structured_data = self._parse_label_value_list(nn_response_text, context="skills response")
            return structured_data
        except ValueError as e: # Catch parsing/validation errors from helper
            print(f"Error processing skills response structure: {e}")
            # Decide: re-raise, return default, or handle differently? Re-raising is often clearest.
            raise Exception(f"Failed to process skills from LLM: {e}") from e
        except Exception as e:
             # Catch other potential errors (_call_api errors are already handled there)
             print(f"Unexpected error processing skills response: {e}")
             raise e


    async def generate_follow_up_questions(self, answers: Dict[str, str]) -> List[str]:
        """Generates follow-up questions based on previous answers using HF Router."""
        # --- This function's logic remains the same, it expects {"questions": [...]} ---
        user_text = "Предыдущие ответы пользователя:\n" + "\n".join(f"- {k}: {v}" for k, v in answers.items())
        user_text += '\n\n---\nНа основе этих ответов, сгенерируй 5-7 УТОЧНЯЮЩИХ вопросов, чтобы глубже понять опыт и навыки кандидата. Верни результат СТРОГО в формате JSON-объекта: {"questions": ["вопрос1", "вопрос2", ...]}. В ответе должен быть ТОЛЬКО JSON-объект и ничего больше.'

        print("Sending request to HF Router for follow-up questions...")
        raw_response = await self._call_api(
            user_text,
            self.settings.FOLLOW_UP_QUESTIONS_PROMPT, # Use specific prompt if defined
            request_json_output=True
        )
        print(f"HF Router Raw JSON String for questions: {raw_response}") # Log raw response

        try:
            cleaned_response = self._clean_llm_json_response(raw_response)
            if not cleaned_response:
                raise json.JSONDecodeError("Empty string received from API after cleaning", cleaned_response, 0)

            questions_data = json.loads(cleaned_response)

            if isinstance(questions_data, dict) and "questions" in questions_data and isinstance(questions_data["questions"], list):
                 questions_list = questions_data["questions"]
                 valid_questions = [str(item) for item in questions_list if isinstance(item, str)]
                 if len(valid_questions) != len(questions_list):
                      print("Warning: 'questions' list contained non-string items. They were filtered out.")
                 if not valid_questions and questions_list: # List existed but had no strings
                      print("Warning: 'questions' list extracted, but contained only non-strings.")
                 elif not valid_questions: # List was empty
                     print("Warning: LLM returned an empty 'questions' list.")

                 return valid_questions
            else:
                 # Handle case where LLM might return just the list directly (less ideal but possible)
                 if isinstance(questions_data, list) and all(isinstance(item, str) for item in questions_data):
                      print("Warning: LLM returned a list directly instead of {'questions': [...]}. Using the list.")
                      return questions_data
                 else:
                     print(f"Error: HF Router returned unexpected JSON structure for questions: {questions_data}")
                     raise ValueError("HF Router did not return a valid JSON object with a 'questions' list of strings.")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for questions: {e}")
            print(f"LLM Raw response string was:\n{raw_response}")
            if 'cleaned_response' in locals(): print(f"String attempted for parsing was:\n{cleaned_response}")
            raise Exception(f"Failed to parse questions from HF Router response (Invalid JSON).") from e
        except ValueError as e: # Catch specific structure errors
             print(f"Error validating questions response structure: {e}")
             raise Exception(f"Failed to validate questions from LLM: {e}") from e
        except Exception as e:
             print(f"Error processing follow-up questions response: {e}")
             raise e


    async def update_resume(self, current_data: List[Any], new_info: str):
        """
        Updates the structured data based on existing data and new user info.
        Receives a list of LabelValueItem objects from the router.
        Returns a list like [{"label": "...", "value": "..."}, ...].
        """
        # Представляем текущие данные LLM в понятном виде
        # Correctly access attributes of LabelValueItem objects
        current_context_parts = []
        for item in current_data:
             # Check if item has the attributes before accessing, good practice
             label = getattr(item, 'label', 'N/A')
             value = getattr(item, 'value', 'N/A')
             current_context_parts.append(f"- {label}: {value}")

        # Or, assuming item will always be LabelValueItem as passed from router:
        # current_context_parts = [f"- {item.label}: {item.value}" for item in current_data]

        current_context_text = "Текущие структурированные данные:\n" + "\n".join(current_context_parts)

        combined_text = f"{current_context_text}\n\nДополнительные инструкции/информация от пользователя для обновления:\n{new_info}"


        # --- Используем промпт, который просит обновить и вернуть В ТОМ ЖЕ ФОРМАТЕ списка ---
        # Используем UPDATE_PROMPT из config.py
        user_prompt_instruction = '\n\n---\nПроанализируй весь приведенный выше текст (текущие данные + инструкции) и верни ОБНОВЛЕННУЮ И ПОЛНУЮ информацию о кандидате СТРОГО в формате JSON-**списка** объектов: `[{"label":"название_поля","value":"обновленное_значение"}, ...]`. Сохраняй релевантные существующие поля, обновляй их или добавляй новые на основе инструкций. В ответе должен быть ТОЛЬКО этот JSON-список.'
        full_user_content = combined_text + user_prompt_instruction

        nn_response_text = await self._call_api(
            full_user_content,
            self.settings.UPDATE_PROMPT, # Ensure this prompt understands context and asks for List[Dict] format
            request_json_output=True
        )
        print(f"Raw JSON String for REGENERATED/UPDATED Data: {nn_response_text}")

        try:
            # --- Используем тот же парсер ---
            updated_structured_data = self._parse_label_value_list(nn_response_text, context="update response")
            return updated_structured_data
        except ValueError as e:
            print(f"Error processing updated data response structure: {e}")
            raise Exception(f"Failed to process updated data from LLM: {e}") from e
        except Exception as e:
             print(f"Unexpected error processing updated data response: {e}")
             raise e
