"""
Tests for backend/voice/tts.py — ElevenLabs text-to-speech.

What we test:
- synthesize_speech() calls ElevenLabs with the right voice ID and model
- Returns audio as bytes
- Uses the multilingual model (supports French + English)
- ElevenLabs client is initialized lazily

ElevenLabs SDK is fully mocked.
"""
import os
from unittest.mock import patch, MagicMock


def test_synthesize_speech_returns_bytes():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"chunk1", b"chunk2"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Hello, I am Chaima.")

    assert isinstance(result, bytes)
    assert result == b"chunk1chunk2"


def test_synthesize_speech_uses_correct_voice_id():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"audio"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        synthesize_speech("Test")

    call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["voice_id"] == os.environ["ELEVENLABS_VOICE_ID"]


def test_synthesize_speech_uses_multilingual_model():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"audio"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        synthesize_speech("Bonjour")

    call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["model_id"] == "eleven_multilingual_v2"


def test_synthesize_speech_passes_text():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"audio"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        synthesize_speech("Chaima est disponible.")

    call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["text"] == "Chaima est disponible."


def test_elevenlabs_client_initialized_lazily():
    with patch("backend.voice.tts._client", None), \
         patch("backend.voice.tts.ElevenLabs") as MockClient:

        mock_instance = MagicMock()
        mock_instance.text_to_speech.convert.return_value = iter([b"audio"])
        MockClient.return_value = mock_instance

        from backend.voice.tts import synthesize_speech
        synthesize_speech("test")

        MockClient.assert_called_once_with(api_key=os.environ["ELEVENLABS_API_KEY"])
