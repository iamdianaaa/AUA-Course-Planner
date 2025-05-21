import json
import os
import re
from typing import List

FOLDER_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
FOLDER_SCRAPED = os.path.join(FOLDER_DATA, "scraped_courses")
FOLDER_REQUIREMENTS = os.path.join(FOLDER_DATA, "requirements")


class PromptGenerator:
    def __init__(self, user_input: str):
        self.user_input = user_input
        prefs = self.extract_preferences(user_input)
        self.program_name = prefs["program_name"]
        self.completed_courses = prefs["completed_courses"]
        self.prefs = prefs

        self.requirements = self._load_json(
            os.path.join(FOLDER_SCRAPED, "aua_courses_all_faculties.json")
        )
        self.semester_courses = self._normalize_semester_courses(
            os.path.join(FOLDER_SCRAPED, "aua_courses_by_semester.json"),
            self.requirements,
        )
        self.degree_requirements = self._load_json(
            os.path.join(FOLDER_REQUIREMENTS, "degree_requirements.json")
        )
        self.program_requirements = self.degree_requirements.get(self.program_name, {})

        self.courses_by_faculty = self._load_json(
            os.path.join(FOLDER_SCRAPED, "courses_by_faculty.json")
        )
        self.faculty_course_codes = {
            c["code"].replace(" ", "")
            for p, courses in self.courses_by_faculty.items()
            if p.lower().replace(" ", "_") == self.program_name
            for c in courses
            if "code" in c
        }

    def _load_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_preferences(self, user_input: str) -> dict:
        prefs = {
            "interests": [],
            "max_credits": None,
            "unavailable_days": [],
            "program_name": None,
            "completed_courses": [],
        }

        input_lower = user_input.lower()

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
            "master of public affairs": 12,
        }

        for program, base_credits in default_base.items():
            if program in input_lower:
                prefs["max_credits"] = base_credits
                prefs["program_name"] = program.replace(" ", "_")
                prefs["raw_program_phrase"] = program.title()
                break
            else:
                match = re.search(
                    r"(?:student in|studying|enrolled in|pursuing|majoring in|doing my|"
                    r"currently in|master in|master of|bachelor in|bachelor of|program in|studies in|"
                    r"from the|specializing in|my degree is in|taking the|part of the)\s+([a-z\s]+)",
                    input_lower,
                )
                prefs["raw_program_phrase"] = (
                    match.group(1).strip().title() if match else "Not recognized"
                )

        if "completed courses" in input_lower:
            codes = re.findall(
                r"(?:bus|ecm|econ|hhm|mgmt|chss|ec|hrsj|"
                r"ird|law|pa|pg|psia|tefl|env|cs|ds|engs|epic|"
                r"ess|iesm|bsn|ph|cbe|cse|fnd|)?\s?\d{3}",
                input_lower,
            )
            prefs["completed_courses"] = [c.upper().replace(" ", "") for c in codes]

        workload_modifiers = {
            "light": 0.6,
            "easy": 0.6,
            "low": 0.6,
            "moderate": 0.8,
            "normal": 0.8,
            "balanced": 0.8,
            "heavy": 1.0,
            "maximum": 1.0,
            "intensive": 1.0,
        }

        prefs["workload_explicitly_mentioned"] = False

        for word, ratio in workload_modifiers.items():
            if word in input_lower and prefs["max_credits"]:
                prefs["max_credits"] = int(prefs["max_credits"] * ratio)
                prefs["workload_explicitly_mentioned"] = True
                break

        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if f"no classes on {day}" in input_lower:
                prefs["unavailable_days"].append(day.capitalize())

        return prefs

    def _normalize_semester_courses(self, path: str, catalog: List[dict]) -> List[dict]:
        raw_courses = self._load_json(path)
        catalog_by_code = {c["code"]: c for c in catalog if "code" in c}
        normalized_courses = []

        for raw in raw_courses:
            text = raw.get("Course", "").strip()
            match = re.search(r"\(([A-Z]{2,4}\d{3})\)$", text)
            code = match.group(1) if match else None
            if not code:
                continue
            title = text.split("\n\n")[0]
            cat = catalog_by_code.get(code, {})
            normalized_courses.append(
                {
                    "code": code,
                    "title": title,
                    "description": cat.get("description", ""),
                    "prerequisites": cat.get("prerequisites", ""),
                    "credits": float(raw.get("Credits", 0)),
                    "raw": raw,
                }
            )

        return normalized_courses

    def _get_required_course_codes(self) -> List[str]:
        entry = self.degree_requirements.get(self.program_name, {})
        codes = re.findall(r"[A-Z]{2,4}\s?\d{3}", entry.get("raw_text", ""))
        return [c.replace(" ", "") for c in codes]

    def _prerequisites_met(self, course: dict) -> bool:
        prereqs = re.findall(r"[A-Z]{2,4}\s?\d{3}", course.get("prerequisites", ""))
        return all(p.replace(" ", "") in self.completed_courses for p in prereqs)

    def filter_courses_by_prerequisites(self) -> List[dict]:
        required = set(self._get_required_course_codes())
        completed = set(self.completed_courses)
        return [
            c
            for c in self.semester_courses
            if self._prerequisites_met(c)
            and c["code"] not in completed
            and c["code"] in required
            and (
                not self.faculty_course_codes or c["code"] in self.faculty_course_codes
            )
        ]

    def build_prompt(self) -> str:
        prefs = self.prefs

        if not self.program_name:
            return (
                "The student's program was not recognized from the input. "
                "Please ask them to specify their degree program.\n\n"
                f"Original user input: {self.user_input}"
            )

        eligible_courses = self.filter_courses_by_prerequisites()

        fallback_note = ""
        if not prefs["workload_explicitly_mentioned"]:
            fallback_note += (
                f"The typical full workload for this program is around {prefs['max_credits']} credits.\n"
                "The student has not specified how heavy they want their schedule to be, "
                "so you may adjust it accordingly based on context.\n\n"
            )

        if not prefs["completed_courses"]:
            fallback_note += (
                "The student has not listed any completed courses. "
                "If necessary, ask the student to confirm them, or proceed cautiously.\n\n"
            )

        return f"""
                You are an intelligent academic advisor.
                
                Based on the following:
                - Degree requirements and course information: {prefs.get('raw_program_phrase', self.program_name.replace('_', ' ').title())}
                - Current semester course offerings (filtered by prerequisites): {eligible_courses}
                - Student interests: {', '.join(prefs['interests']) or 'Not specified'}
                - Preferred workload: {prefs['max_credits'] or 'Not specified'} credits
                - Completed courses: {', '.join(self.completed_courses) or 'None'}
                - Unavailable days: {', '.join(prefs['unavailable_days']) or 'None'}
                
                If any required field seems unclear, also use the original user input below for context:
                "{self.user_input}"
                
                Generate an optimized course plan for this semester.
                List course codes, course names, number of credits, and give a short reason for each choice.
                Ensure prerequisites are respected and the total credits do not exceed the student's preferred limit.
                        """.strip()
