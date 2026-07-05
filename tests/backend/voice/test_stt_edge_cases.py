"""
Edge case and error handling tests for backend/voice/stt.py
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open


def test_transcribe_audio_raises_on_whisper_failure():
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("model inference failed")

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        with pytest.raises(RuntimeError, match="model inference failed"):
            transcribe_audio(b"audio bytes")


def test_transcribe_audio_raises_on_model_load_failure():
    with patch("backend.voice.stt._model", None), \
         patch("backend.voice.stt.whisper") as MockWhisper, \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        MockWhisper.load_model.side_effect = Exception("model download failed")

        from backend.voice.stt import transcribe_audio
        with pytest.raises(Exception, match="model download failed"):
            transcribe_audio(b"audio bytes")


def test_transcribe_audio_returns_empty_string_when_whisper_returns_empty():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "   "}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"silence")

        assert result == ""


def test_transcribe_audio_passes_fp16_false():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "hello"}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"audio")

        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs.get("fp16") is False


def test_transcribe_audio_handles_french_output():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Bonjour, je m'appelle Chaima."}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"french audio", language="fr")

        assert result == "Bonjour, je m'appelle Chaima."


def test_transcribe_audio_with_english_language_param():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Hello, my name is Chaima."}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        transcribe_audio(b"english audio", language="en")

        call_kwargs = mock_model.transcribe.call_args.kwargs
        assert call_kwargs.get("language") == "en"


def test_transcribe_audio_handles_empty_bytes():
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": ""}

    with patch("backend.voice.stt._model", mock_model), \
         patch("tempfile.NamedTemporaryFile", mock_open()):

        from backend.voice.stt import transcribe_audio
        result = transcribe_audio(b"")

        assert result == ""
