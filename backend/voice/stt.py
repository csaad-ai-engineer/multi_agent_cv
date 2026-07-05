"""
STT client — forwards audio to the host voice service (port 8002).
Whisper runs on the host with MPS access instead of CPU inside the container.
"""
import os
import httpx

VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://host.docker.internal:8002")


def transcribe_audio(audio_bytes: bytes) -> str:
    response = httpx.post(
        f"{VOICE_SERVICE_URL}/stt",
        files={"audio": ("recording.webm", audio_bytes, "audio/webm")},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["text"]
