from flask import Blueprint, request, jsonify
from src.external.prompt_generator import PromptGenerator

planner_bp = Blueprint('planner_bp', __name__)


@planner_bp.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    user_input = request.json.get("user_input", "")

    generator = PromptGenerator(
        requirements_path="../../data/requirements/degree_requirements.json",
        completed_courses_path="../../data/completed/completed_courses.json",
        semester_courses_path="../../data/scraped_courses/aua_courses_by_semester.json"
    )

    prompt = generator.build_prompt(user_input)

    return jsonify({"prompt": prompt})
