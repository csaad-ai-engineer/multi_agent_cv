"""
Tests for backend/voice/stt.py — Whisper speech-to-text.

What we test:
- transcribe_audio() writes audio to a temp file and calls whisper
- Language parameter is passed when provided
- Returns the transcribed text string
- The whisper model is loaded lazily (only once)

Whisper is mocked — no model download needed.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open


def test_transcribe_audio_returns_text():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "  Bonjour, comment ça va ?  "}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"fake audio bytes")

        assert result == "Bonjour, comment ça va ?"  # stripped


def test_transcribe_audio_with_language():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Hello"}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio", language="fr")

        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs.get("language") == "fr"


def test_transcribe_audio_without_language_omits_param():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Hello"}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio")

        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert "language" not in call_kwargs


def test_whisper_model_loaded_lazily():
    with patch("backend.voice.stt._model", None), \
         patch("backend.voice.stt.whisper") as MockWhisper, \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "test"}
        MockWhisper.load_model.return_value = mock_model

        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio")

        MockWhisper.load_model.assert_called_once_with("base")


def test_transcribe_audio_strips_whitespace():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "   hello world   "}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"audio")

        assert result == "hello world"
