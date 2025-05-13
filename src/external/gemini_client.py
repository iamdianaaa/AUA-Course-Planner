from google import generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from .prompt_generator import PromptGenerator


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro-exp-03-25", history: list = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = self.model.start_chat(history=history or [])

    def start_conversation(self, user_input: str) -> str:
        try:
            self.chat = self.model.start_chat()
            prompt_generator = PromptGenerator(user_input)
            prompt = prompt_generator.build_prompt()
            return self.send_message(prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to start conversation: {e}")

    def send_message(self, message: str) -> str:
        try:
            if not self.chat:
                self.chat = self.model.start_chat()
            response = self.chat.send_message(message)
            return response.text.strip()
        except GoogleAPIError as e:
            raise RuntimeError(f"Google API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")

    def continue_conversation(self, follow_up_message: str) -> str:
        return self.send_message(follow_up_message)

    def reset_chat(self):
        try:
            self.chat = self.model.start_chat()
        except Exception as e:
            raise RuntimeError(f"Failed to reset chat: {e}")

    def get_history(self):
        return [
            {
                "role": msg.role,
                "parts": [part.text for part in msg.parts]
            }
            for msg in self.chat.history
        ]