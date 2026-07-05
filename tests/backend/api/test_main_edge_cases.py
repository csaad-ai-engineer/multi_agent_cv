"""
Edge case and error handling tests for backend/api/main.py
"""
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def _make_client(raise_server_exceptions=True):
    """Import and return a TestClient for the FastAPI app.

    We clear the 'multipart' MagicMock stub first so FastAPI can find the
    real python-multipart package needed for UploadFile routing.
    """
    for key in list(sys.modules):
        if "multipart" in key:
            del sys.modules[key]

    with patch("backend.core.graph.build_graph") as MockBuild:
        MockBuild.return_value = MagicMock()
        from backend.api.main import app
        return TestClient(app, raise_server_exceptions=raise_server_exceptions)


@pytest.fixture
def client():
    return _make_client()


@pytest.fixture
def client_no_raise():
    return _make_client(raise_server_exceptions=False)


def test_chat_endpoint_with_empty_question(client):
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"answer": "Please provide a question.", "route": "cv_rag"}
        response = client.post("/chat", json={"question": ""})

    assert response.status_code == 200
    assert response.json()["answer"] == "Please provide a question."


def test_chat_endpoint_with_very_long_question(client):
    long_question = "Tell me about Chaima. " * 300
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"answer": "She is an AI engineer.", "route": "cv_rag"}
        response = client.post("/chat", json={"question": long_question})

    assert response.status_code == 200
    MockGraph.invoke.assert_called_once_with({"question": long_question})


def test_chat_endpoint_rejects_invalid_json(client):
    response = client.post(
        "/chat",
        content="not valid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_chat_endpoint_returns_500_on_graph_exception(client_no_raise):
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.side_effect = Exception("graph internal error")
        response = client_no_raise.post("/chat", json={"question": "What are her skills?"})

    assert response.status_code == 500


def test_chat_response_includes_route_field(client):
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"answer": "answer", "route": "projects"}
        response = client.post("/chat", json={"question": "What projects did she build?"})

    assert response.json()["route"] == "projects"


def test_chat_response_route_defaults_to_empty_string_when_missing(client):
    with patch("backend.core.graph.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"answer": "some answer"}
        response = client.post("/chat", json={"question": "Tell me about yourself."})

    assert response.status_code == 200
    assert response.json()["route"] == ""


def test_voice_stt_requires_audio_file(client):
    response = client.post("/voice/stt")
    assert response.status_code in (400, 422)



def test_voice_tts_with_empty_text(client):
    with patch("backend.api.main.synthesize_speech") as MockTTS:
        MockTTS.return_value = b""
        response = client.post("/voice/tts", json={"question": ""})

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"


def test_voice_tts_returns_500_on_synthesis_failure(client_no_raise):
    with patch("backend.api.main.synthesize_speech") as MockTTS:
        MockTTS.side_effect = Exception("ElevenLabs quota exceeded")
        response = client_no_raise.post("/voice/tts", json={"question": "Hello"})

    assert response.status_code == 500
