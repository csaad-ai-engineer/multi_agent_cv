"""
Edge case and error handling tests for backend/voice/stt.py
"""
from unittest.mock import patch, MagicMock


def test_transcribe_audio_uses_custom_voice_service_url(monkeypatch):
    monkeypatch.setenv("VOICE_SERVICE_URL", "http://custom-host:9999")
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "test"}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response) as mock_post:
        import importlib
        import backend.voice.stt as stt
        importlib.reload(stt)

        stt.transcribe_audio(b"audio")

    assert mock_post.call_args.args[0] == "http://custom-host:9999/stt"


def test_transcribe_audio_uses_timeout():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "test"}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio")

    assert mock_post.call_args.kwargs["timeout"] == 120


def test_transcribe_audio_handles_french_output():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "Bonjour, je m'appelle Chaima."}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response):
        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"french audio")

    assert result == "Bonjour, je m'appelle Chaima."

def test_transcribe_audio_sends_webm_content_type():
    mock_response = MagicMock(status_code=200)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"text": "hello"}

    with patch("backend.voice.stt.httpx.post", return_value=mock_response) as mock_post:
        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio")

    _, _, content_type = mock_post.call_args.kwargs["files"]["audio"]
    assert content_type == "audio/webm"
