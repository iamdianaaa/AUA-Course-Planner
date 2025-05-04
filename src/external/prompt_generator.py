import json
import os
from typing import Optional


class PromptGenerator:
    """
    Builds a Gemini-compatible prompt using student input,
    degree requirements, available semester courses, and completed courses.
    """

    def __init__(self,
                 requirements_path: str,
                 completed_courses_path: Optional[str] = None,
                 semester_courses_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.requirements_path = os.path.join(base_dir, requirements_path)
        self.semester_courses_path = os.path.join(base_dir, semester_courses_path or "../../data/scraped_courses/aua_courses_by_semester.json")
        self.completed_courses_path = os.path.join(base_dir, completed_courses_path) if completed_courses_path else None

        self.requirements = self._load_json(self.requirements_path)
        self.semester_courses = self._load_json(self.semester_courses_path)
        self.completed_courses = self._load_json(self.completed_courses_path) if self.completed_courses_path else []

    def _load_json(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_preferences(self, user_input: str) -> dict:
        """
        Parses user input for workload preference, unavailable days, and potential program mentions.
        """
        prefs = {
            "interests": [],
            "max_credits": None,
            "unavailable_days": []
        }

        input_lower = user_input.lower()

        # Default full-time credits per program
        default_base = {
            "ll.m.": 9,
            "llm": 9,
            "master of laws": 9,
            "ma hrsj": 12,
            "human rights and social justice": 12,
            "master of arts in human rights and social justice": 12,
            "ma tefl": 12,
            "tefl": 12,
            "master of arts in teaching english as a foreign language": 12,
            "mse": 9,
            "master of science in economics": 9,
            "mba": 11,
            "master of business administration": 11,
            "msm": 15,
            "master of science in management": 15,
            "me iesm": 15,
            "ms iesm": 15,
            "master of engineering in industrial engineering & systems management": 15,
            "ms cis": 15,
            "cis": 15,
            "computer and information science": 15,
            "mph": 18,
            "public health": 18,
            "master of public health": 18,
            "maird": 12,
            "international relations and diplomacy": 12,
            "master of arts in international relations and diplomacy": 12,
            "mpa": 12,
            "master of public affairs": 12
        }

        for program, base_credits in default_base.items():
            if program in input_lower:
                prefs["max_credits"] = base_credits
                break

        # Adjust workload by synonyms
        workload_modifiers = {
            "light": 0.6,
            "easy": 0.6,
            "low": 0.6,
            "moderate": 0.8,
            "normal": 0.8,
            "balanced": 0.8,
            "heavy": 1.0,
            "maximum": 1.0,
            "intensive": 1.0
        }

        for word, ratio in workload_modifiers.items():
            if word in input_lower:
                if prefs["max_credits"]:
                    prefs["max_credits"] = int(prefs["max_credits"] * ratio)
                break

        # Extract unavailable days
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if f"no classes on {day}" in input_lower:
                prefs["unavailable_days"].append(day.capitalize())

        return prefs

    def build_prompt(self, user_input: str) -> str:
        """
        Constructs a final prompt string for Gemini based on the extracted preferences.
        """
        prefs = self.extract_preferences(user_input)

        return f"""
You are an intelligent academic advisor.

Based on the following:
- Degree requirements and course information: {self.requirements}
- Current semester course offerings: {self.semester_courses}
- Student interests: {', '.join(prefs['interests']) or 'Not specified'}
- Preferred workload: {prefs['max_credits'] or 'Not specified'} credits
- Completed courses: {', '.join(self.completed_courses) or 'None'}
- Unavailable days: {', '.join(prefs['unavailable_days']) or 'None'}

Generate an optimized course plan for this semester.
List course codes, course names, number of credits, and give a short reason for each choice.
Ensure prerequisites are respected and the total credits do not exceed the student's preferred limit.
        """.strip()
