from flask import Blueprint, request
from src.external.gemini_client import GeminiClient
from src.config import AppConfig
from src.models.chat import ChatResponse, ErrorResponse
from src.services.session_store import RedisSessionStore
from http import HTTPStatus

planner_bp = Blueprint("planner", __name__)

session_store = RedisSessionStore()


@planner_bp.route("/start_chat", methods=["POST"])
def start_chat():
    data = request.get_json()
    user_id = data.get("user_id")
    user_input = data.get("user_input")

    if not user_id or not user_input:
        return ErrorResponse(error="user_id and message required").model_dump(), HTTPStatus.BAD_REQUEST

    try:
        client = GeminiClient(api_key=AppConfig.GEMINI.API_KEY, model_name=AppConfig.GEMINI.MODEL_NAME)
        response = client.start_conversation(user_input)

        session_store.set_session(user_id, client.get_history())
        return ChatResponse(response=response).model_dump(), HTTPStatus.OK
    except Exception as e:
        return ErrorResponse(error=f"Something went wrong {e}").model_dump(), HTTPStatus.INTERNAL_SERVER_ERROR


@planner_bp.route("/continue_chat", methods=["POST"])
def continue_chat():
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")

    history = session_store.get_session(user_id)
    if not history or not isinstance(history, list):
        return ErrorResponse(error="Invalid or missing chat history").model_dump(), HTTPStatus.NOT_FOUND

    try:
        client = GeminiClient(api_key=AppConfig.GEMINI.API_KEY, model_name=AppConfig.GEMINI.MODEL_NAME, history=history)
        response = client.continue_conversation(message)

        session_store.set_session(user_id, client.get_history())
        return ChatResponse(response=response).model_dump(), HTTPStatus.OK
    except Exception as e:
        return ErrorResponse(error=f"Something went wrong {e}").model_dump(), HTTPStatus.INTERNAL_SERVER_ERROR


@planner_bp.route("/reset_chat", methods=["POST"])
def reset_chat():
    data = request.get_json()
    user_id = data.get("user_id")

    if session_store.get_session(user_id):
        session_store.delete_session(user_id)
        return ChatResponse(response="Chat reset").model_dump(), HTTPStatus.OK

    return ErrorResponse(error="User session not found").model_dump(), HTTPStatus.NOT_FOUND
