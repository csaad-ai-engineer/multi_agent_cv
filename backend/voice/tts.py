"""
TTS client — forwards text to the host voice service (port 8002).
Coqui XTTS v2 runs on the host with MPS access instead of CPU inside the container.
"""
import os
import httpx

VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://host.docker.internal:8002")


def synthesize_speech(text: str) -> bytes:
    response = httpx.post(
        f"{VOICE_SERVICE_URL}/tts",
        json={"question": text},
        timeout=120,
    )
    if response.status_code == 400:
        raise ValueError(response.json().get("detail", "TTS error"))
    response.raise_for_status()
    return response.content
