from flask import Blueprint

planner_bp = Blueprint('planner', __name__)


@planner_bp.route('/plan', methods=['POST'])
def plan():
    return {"status": "ok"}
