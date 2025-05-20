from flask import Blueprint, request
from src.external.gemini_client import GeminiClient
from src.config import AppConfig
from src.models.chat import ChatResponse, ErrorResponse, ChatHistoryResponse
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
        return (
            ErrorResponse(error="user_id and message required").model_dump(),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        client = GeminiClient(
            api_key=AppConfig.GEMINI.API_KEY, model_name=AppConfig.GEMINI.MODEL_NAME
        )
        response = client.start_conversation(user_input)

        session_store.set_session(
            user_id,
            {
                "raw_history": [
                    {"role": "user", "parts": [user_input]},
                    {"role": "model", "parts": [response]},
                ],
                "gemini_history": client.get_history(),
            },
        )

        return ChatResponse(response=response).model_dump(), HTTPStatus.OK
    except Exception as e:
        return (
            ErrorResponse(error=f"Something went wrong {e}").model_dump(),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@planner_bp.route("/continue_chat", methods=["POST"])
def continue_chat():
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")

    history = session_store.get_session(user_id)
    if not history:
        return (
            ErrorResponse(error="Invalid or missing chat history").model_dump(),
            HTTPStatus.NOT_FOUND,
        )

    try:
        gemini_history = history.get("gemini_history", [])
        raw_history = history.get("raw_history", [])

        client = GeminiClient(
            api_key=AppConfig.GEMINI.API_KEY,
            model_name=AppConfig.GEMINI.MODEL_NAME,
            history=gemini_history,
        )
        response = client.continue_conversation(message)

        raw_history.append({"role": "user", "parts": [message]})
        raw_history.append({"role": "model", "parts": [response]})

        session_store.set_session(
            user_id,
            {"raw_history": raw_history, "gemini_history": client.get_history()},
        )
        return ChatResponse(response=response).model_dump(), HTTPStatus.OK
    except Exception as e:
        return (
            ErrorResponse(error=f"Something went wrong {e}").model_dump(),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@planner_bp.route("/reset_chat", methods=["POST"])
def reset_chat():
    data = request.get_json()
    user_id = data.get("user_id")

    if session_store.get_session(user_id):
        session_store.delete_session(user_id)
        return ChatResponse(response="Chat reset").model_dump(), HTTPStatus.OK

    return (
        ErrorResponse(error="User session not found").model_dump(),
        HTTPStatus.NOT_FOUND,
    )


@planner_bp.route("/chat_history", methods=["GET"])
def get_chat_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return (
            ErrorResponse(error="user_id is required").model_dump(),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        history = session_store.get_raw_history(user_id)
        if not history:
            return (
                ErrorResponse(error="No chat history found for this user").model_dump(),
                HTTPStatus.NOT_FOUND,
            )

        response_model = ChatHistoryResponse(user_id=user_id, history=history)
        return response_model.model_dump(), HTTPStatus.OK
    except Exception as e:
        return (
            ErrorResponse(error=f"Failed to retrieve chat history: {e}").model_dump(),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
