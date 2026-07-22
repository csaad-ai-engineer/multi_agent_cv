"""
Edge case and error handling tests for backend/voice/tts.py
"""
from unittest.mock import patch, MagicMock

import pytest


def test_synthesize_speech_uses_custom_voice_service_url(monkeypatch):
    monkeypatch.setenv("VOICE_SERVICE_URL", "http://custom-host:9999")
    mock_response = MagicMock(status_code=200, content=b"audio")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        import importlib
        import backend.voice.tts as tts
        importlib.reload(tts)

        tts.synthesize_speech("test")

    assert mock_post.call_args.args[0] == "http://custom-host:9999/tts"


def test_synthesize_speech_uses_timeout():
    mock_response = MagicMock(status_code=200, content=b"audio")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.tts import synthesize_speech
        synthesize_speech("test")

    assert mock_post.call_args.kwargs["timeout"] == 120


def test_synthesize_speech_400_without_detail_uses_fallback_message():
    mock_response = MagicMock(status_code=400)
    mock_response.json.return_value = {}

    with patch("backend.voice.tts.httpx.post", return_value=mock_response):
        from backend.voice.tts import synthesize_speech
        with pytest.raises(ValueError, match="TTS error"):
            synthesize_speech("test")


def test_synthesize_speech_with_french_text():
    mock_response = MagicMock(status_code=200, content=b"chunk_fr")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Bonjour, je suis Chaima.")

    assert mock_post.call_args.kwargs["json"]["question"] == "Bonjour, je suis Chaima."
    assert result == b"chunk_fr"
