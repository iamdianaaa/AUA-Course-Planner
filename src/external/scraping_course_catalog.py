import requests
import json
import os
import re
from bs4 import BeautifulSoup
from collections import defaultdict


class CourseScraper:
    def __init__(self, url="https://catalog.aua.am/course-descriptions-2024/"):
        self.url = url
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.raw_output_file = os.path.join(
            base_dir, "..", "data", "scraped_courses", "aua_courses_all_faculties.json"
        )
        self.grouped_output_file = os.path.join(
            base_dir, "..", "data", "scraped_courses", "courses_by_faculty.json"
        )
        self.courses = []

    def scrape_courses(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch page: {self.url}")

        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = [
            p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)
        ]

        course_chunks = []
        current_chunk = []
        code_pattern = re.compile(r"^[A-Z]{2,4}\d{3}$")

        for text in paragraphs:
            if code_pattern.match(text):
                if current_chunk:
                    course_chunks.append(current_chunk)
                current_chunk = [text]
            else:
                current_chunk.append(text)
        if current_chunk:
            course_chunks.append(current_chunk)

        current_faculty = "Unknown"
        for chunk in course_chunks:
            code = chunk[0]
            title = ""
            description = ""
            credits = None
            prerequisites = ""
            faculty = current_faculty

            for line in chunk[1:]:
                if line.isupper() and not code_pattern.match(line):
                    faculty = line
                    current_faculty = faculty
                    continue
                if not title:
                    title = line
                elif "Credits:" in line:
                    try:
                        credits = float(line.split("Credits:")[1].strip())
                    except:
                        credits = None
                elif "Prerequisite" in line:
                    if ":" in line:
                        prerequisites += line.split(":", 1)[1].strip() + " "
                    else:
                        prerequisites += line.strip() + " "
                else:
                    description += line + " "

            self.courses.append(
                {
                    "faculty": faculty,
                    "code": code,
                    "title": title,
                    "description": description.strip(),
                    "credits": credits,
                    "prerequisites": prerequisites.strip(),
                }
            )

        self._save_to_file(self.raw_output_file, self.courses)
        # print(f"Scraped {len(self.courses)} courses and saved to:\n{self.raw_output_file}")

    def group_by_faculty(self):
        if not os.path.exists(self.raw_output_file):
            raise FileNotFoundError(f"Input file not found at {self.raw_output_file}")

        with open(self.raw_output_file, "r", encoding="utf-8") as f:
            all_courses = json.load(f)

        grouped = defaultdict(list)
        for course in all_courses:
            faculty = course.get("faculty", "Unknown")
            grouped[faculty].append(course)

        self._save_to_file(self.grouped_output_file, grouped)
        # print(f"Grouped courses by faculty and saved to:\n{self.grouped_output_file}")

    def _save_to_file(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
