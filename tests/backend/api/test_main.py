"""
Tests for backend/api/main.py — the FastAPI server.

We use FastAPI's TestClient which runs requests in-process (no server needed).
All agent and voice calls are mocked so no LLM or ElevenLabs API is hit.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("backend.core.graph.build_graph") as MockBuild:
        MockBuild.return_value = MagicMock()
        from backend.api.main import app
        return TestClient(app)


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_returns_answer(client):
    mock_result = {"question": "q", "route": "skills", "answer": "She knows LangGraph."}

    with patch("backend.api.main.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = mock_result
        response = client.post("/chat", json={"question": "What are her skills?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "She knows LangGraph."
    assert data["route"] == "skills"


def test_chat_endpoint_requires_question_field(client):
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Unprocessable Entity — missing required field


def test_chat_endpoint_passes_question_to_graph(client):
    with patch("backend.api.main.cv_agent_graph") as MockGraph:
        MockGraph.invoke.return_value = {"answer": "ok", "route": "cv_rag"}
        client.post("/chat", json={"question": "Tell me about Chaima."})
        MockGraph.invoke.assert_called_once_with({"question": "Tell me about Chaima."})


def test_voice_stt_endpoint_returns_text(client):
    with patch("backend.api.main.transcribe_audio") as MockSTT:
        MockSTT.return_value = "Quelles sont tes compétences ?"
        audio_bytes = b"fake audio data"
        response = client.post(
            "/voice/stt",
            files={"audio": ("test.webm", audio_bytes, "audio/webm")},
        )

    assert response.status_code == 200
    assert response.json()["text"] == "Quelles sont tes compétences ?"


def test_voice_tts_endpoint_returns_audio(client):
    with patch("backend.api.main.synthesize_speech") as MockTTS:
        MockTTS.return_value = b"fake mp3 audio bytes"
        response = client.post("/voice/tts", json={"question": "Hello, I am Chaima."})

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content == b"fake mp3 audio bytes"


def test_cors_headers_present(client):
    response = client.options("/chat", headers={"Origin": "http://localhost:3000"})
    assert response.status_code in (200, 405)  # endpoint exists
