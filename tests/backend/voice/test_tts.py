"""
Tests for backend/voice/tts.py — TTS client that proxies to the host voice service.

What we test:
- synthesize_speech() posts the text to the voice service /tts endpoint
- Returns the audio response content as bytes
- Raises ValueError with the service's detail message on a 400 response
- Raises on other HTTP errors via raise_for_status()

httpx is mocked — no network calls, no voice service needed.
"""
from unittest.mock import patch, MagicMock

import pytest


def test_synthesize_speech_returns_bytes():
    mock_response = MagicMock(status_code=200, content=b"audio-bytes")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Hello, I am Chaima.")

    assert isinstance(result, bytes)
    assert result == b"audio-bytes"
    mock_post.assert_called_once()


def test_synthesize_speech_posts_to_tts_endpoint_with_question():
    mock_response = MagicMock(status_code=200, content=b"audio")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.tts import synthesize_speech
        synthesize_speech("Bonjour, je suis Chaima.")

    args, kwargs = mock_post.call_args
    assert args[0].endswith("/tts")
    assert kwargs["json"] == {"question": "Bonjour, je suis Chaima."}


def test_synthesize_speech_raises_value_error_on_400():
    mock_response = MagicMock(status_code=400)
    mock_response.json.return_value = {"detail": "Text too long"}

    with patch("backend.voice.tts.httpx.post", return_value=mock_response):
        from backend.voice.tts import synthesize_speech
        with pytest.raises(ValueError, match="Text too long"):
            synthesize_speech("some text")


def test_synthesize_speech_raises_on_http_error():
    mock_response = MagicMock(status_code=500)
    mock_response.raise_for_status.side_effect = Exception("Server error")

    with patch("backend.voice.tts.httpx.post", return_value=mock_response):
        from backend.voice.tts import synthesize_speech
        with pytest.raises(Exception, match="Server error"):
            synthesize_speech("some text")


def test_synthesize_speech_with_empty_text():
    mock_response = MagicMock(status_code=200, content=b"")
    mock_response.raise_for_status.return_value = None

    with patch("backend.voice.tts.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("")

    assert result == b""
    assert mock_post.call_args.kwargs["json"] == {"question": ""}
