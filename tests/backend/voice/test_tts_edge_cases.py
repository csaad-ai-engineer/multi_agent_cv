"""
Edge case and error handling tests for backend/voice/tts.py
"""
import pytest
from unittest.mock import patch, MagicMock


def test_synthesize_speech_raises_on_elevenlabs_api_failure():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.side_effect = Exception("ElevenLabs API error")

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        with pytest.raises(Exception, match="ElevenLabs API error"):
            synthesize_speech("Hello")


def test_synthesize_speech_with_empty_generator_returns_empty_bytes():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Hello")

    assert result == b""


def test_synthesize_speech_with_empty_text():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"audio"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("")

    call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["text"] == ""
    assert isinstance(result, bytes)


def test_synthesize_speech_voice_settings_values():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"audio"])

    with patch("backend.voice.tts._client", mock_client), \
         patch("backend.voice.tts.VoiceSettings") as MockVoiceSettings:

        from backend.voice.tts import synthesize_speech
        synthesize_speech("test")

        MockVoiceSettings.assert_called_once_with(
            stability=0.5,
            similarity_boost=0.8,
            style=0.2,
            use_speaker_boost=True,
        )


def test_synthesize_speech_with_french_text():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"chunk_fr"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Bonjour, je suis Chaima.")

    call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
    assert call_kwargs["text"] == "Bonjour, je suis Chaima."
    assert result == b"chunk_fr"


def test_synthesize_speech_raises_on_client_init_failure():
    with patch("backend.voice.tts._client", None), \
         patch("backend.voice.tts.ElevenLabs") as MockClient:

        MockClient.side_effect = Exception("invalid API key")

        from backend.voice.tts import synthesize_speech
        with pytest.raises(Exception, match="invalid API key"):
            synthesize_speech("Hello")


def test_synthesize_speech_concatenates_multiple_chunks():
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = iter([b"part1", b"part2", b"part3"])

    with patch("backend.voice.tts._client", mock_client):
        from backend.voice.tts import synthesize_speech
        result = synthesize_speech("Long text response.")

    assert result == b"part1part2part3"
