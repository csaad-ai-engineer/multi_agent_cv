"""
Tests for backend/voice/stt.py — STT client that proxies to the host voice service.

What we test:
- transcribe_audio() posts the audio bytes to the voice service /stt endpoint
- Returns the transcribed text string from the JSON response
- Raises on HTTP errors via raise_for_status()

httpx is mocked — no network calls, no voice service needed.
"""
from unittest.mock import patch, MagicMock

import pytest


def test_transcribe_audio_returns_text():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "Bonjour, comment ça va ?"}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response):
        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"fake audio bytes")

    assert result == "Bonjour, comment ça va ?"


def test_transcribe_audio_posts_to_stt_endpoint_with_audio_file():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "Hello"}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio bytes")

    args, kwargs = mock_post.call_args
    assert args[0].endswith("/stt")
    filename, content, content_type = kwargs["files"]["audio"]
    assert filename == "recording.webm"
    assert content == b"audio bytes"
    assert content_type == "audio/webm"


def test_transcribe_audio_raises_on_http_error():
    mock_response = MagicMock(status_code=500)
    mock_response.raise_for_status.side_effect = Exception("Server error")

    with patch("backend.voice.stt.httpx.post", return_value=mock_response):
        from backend.voice.stt import transcribe_audio
        with pytest.raises(Exception, match="Server error"):
            transcribe_audio(b"audio bytes")


def test_transcribe_audio_handles_empty_bytes():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": ""}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response):
        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"")

    assert result == ""
