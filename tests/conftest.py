import pytest
from src import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_start_response():
    return "Mocked Gemini start response"

@pytest.fixture
def mock_continue_response():
    return "Mocked Gemini continue response"

@pytest.fixture
def mock_history():
    return [
        {"role": "user", "parts": ["Hi, I'm a student."]},
        {"role": "model", "parts": ["Hello! What program are you in?"]}
    ]
