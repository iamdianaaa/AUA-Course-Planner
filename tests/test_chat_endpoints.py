from unittest.mock import patch

@patch("src.controllers.planner.GeminiClient")
@patch("src.controllers.planner.session_store")
def test_start_chat_success(mock_store, mock_gemini, client, mock_start_response, mock_history):
    mock_client_instance = mock_gemini.return_value
    mock_client_instance.start_conversation.return_value = mock_start_response
    mock_client_instance.get_history.return_value = mock_history

    payload = {
        "user_id": "test_user",
        "user_input": "I'm a student in MS IESM"
    }

    response = client.post("/api/start_chat", json=payload)

    assert response.status_code == 200
    assert response.get_json()["response"] == mock_start_response
    mock_store.set_session.assert_called_once()


@patch("src.controllers.planner.GeminiClient")
@patch("src.controllers.planner.session_store")
def test_continue_chat_success(mock_store, mock_gemini, client, mock_continue_response, mock_history):
    mock_store.get_session.return_value = {
        "gemini_history": mock_history,
        "raw_history": mock_history.copy(),
    }
    mock_client_instance = mock_gemini.return_value
    mock_client_instance.continue_conversation.return_value = mock_continue_response
    mock_client_instance.get_history.return_value = mock_history

    payload = {
        "user_id": "test_user",
        "message": "What courses can I take?"
    }

    response = client.post("/api/continue_chat", json=payload)

    assert response.status_code == 200
    assert response.get_json()["response"] == mock_continue_response
    mock_store.set_session.assert_called_once()


@patch("src.controllers.planner.session_store")
def test_reset_chat_success(mock_store, client, mock_history):
    mock_store.get_session.return_value = mock_history

    response = client.post("/api/reset_chat", json={"user_id": "test_user"})

    assert response.status_code == 200
    assert response.get_json()["response"] == "Chat reset"
    mock_store.delete_session.assert_called_once()


@patch("src.controllers.planner.session_store")
def test_start_chat_missing_input(mock_store, client):
    response = client.post("/api/start_chat", json={"user_id": "abc"})
    assert response.status_code == 400
    assert "user_id and message required" in response.get_json()["error"]


@patch("src.controllers.planner.session_store")
def test_get_chat_history_success(mock_store, client, mock_history):
    mock_store.get_raw_history.return_value = mock_history
    user_id = "test_user"

    response = client.get(f"/api/chat_history?user_id={user_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["user_id"] == user_id
    assert data["history"] == mock_history
    mock_store.get_raw_history.assert_called_once_with(user_id)


@patch("src.controllers.planner.session_store")
def test_get_chat_history_missing_user_id(mock_store, client):
    response = client.get("/api/chat_history")

    assert response.status_code == 400
    assert "user_id is required" in response.get_json()["error"]


@patch("src.controllers.planner.session_store")
def test_get_chat_history_not_found(mock_store, client):
    mock_store.get_raw_history.return_value = None

    response = client.get("/api/chat_history?user_id=unknown_user")

    assert response.status_code == 404
    assert "No chat history found" in response.get_json()["error"]
