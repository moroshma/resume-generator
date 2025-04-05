import requests
from ai_service.config import Settings

class NeuralService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.headers = {
            "Authorization": f"Bearer {self.settings.API_KEY}",
            "Content-Type": "application/json"
        }

    def _call_api(self, user_content: str) -> str:
        data = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {"role": "system", "content": self.settings.SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(
            self.settings.API_URL,
            json=data,
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        raise Exception(f"API Error: {response.status_code}")

    def process_answers(self, answers: dict) -> dict:
        user_text = "\n".join(f"{k}: {v}" for k, v in answers.items())
        nn_response = self._call_api(user_text)
        return {
            "experience": "Ваш опыт, извлеченный из ответов",
            "hard_skills": nn_response
        }

    def update_resume(self, current_text: str, new_info: str) -> dict:
        updated_content = f"{current_text}\n{new_info}"
        nn_response = self._call_api(updated_content)
        return {"updated_hard_skills": nn_response}
