from google import generativeai as genai
from prompt_generator import PromptGenerator


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-pro-exp-03-25"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = None

    def start_conversation(self, user_input: str) -> str:
        self.chat = self.model.start_chat()
        prompt_generator = PromptGenerator(user_input)
        prompt = prompt_generator.build_prompt()
        return self.send_message(prompt)

    def send_message(self, message: str) -> str:
        if not self.chat:
            self.chat = self.model.start_chat()
        response = self.chat.send_message(message)
        return response.text.strip()

    def continue_conversation(self, follow_up_message: str) -> str:
        return self.send_message(follow_up_message)

    def reset_chat(self):
        self.chat = self.model.start_chat()

    def get_chat_history(self):
        return [(msg.role, msg.parts[0].text) for msg in self.chat.history]
