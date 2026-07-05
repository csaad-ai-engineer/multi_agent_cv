"""
Voice service — runs on the HOST machine for MPS/GPU access.
Exposes STT (Whisper) and TTS (Coqui XTTS v2) as HTTP endpoints on port 8002.

Start with:
    python3 voice_service.py
"""
import io
import os
import re
import tempfile

import torch
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    _get_whisper()
    _get_conditioning_latents()
    print("Voice service ready.")
    yield

app = FastAPI(title="Voice Service", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------
def _best_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

DEVICE = _best_device()
print(f"Voice service using device: {DEVICE}")

# ---------------------------------------------------------------------------
# STT — Whisper
# ---------------------------------------------------------------------------
_whisper_model = None

def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print("Loading Whisper model...")
        _whisper_model = whisper.load_model("base", device=DEVICE)
        print("Whisper ready.")
    return _whisper_model


def _transcribe(audio_bytes: bytes) -> str:
    model = _get_whisper()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        result = model.transcribe(tmp_path, fp16=(DEVICE != "cpu"))
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)


@app.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    text = _transcribe(audio_bytes)
    return {"text": text}


# ---------------------------------------------------------------------------
# TTS — Coqui XTTS v2
# ---------------------------------------------------------------------------
VOICE_SAMPLE = os.getenv("VOICE_SAMPLE_PATH", "voice_data/voice_sample.mp3")
MAX_WORDS = 60

_tts_model = None
_gpt_cond_latent = None
_speaker_embedding = None


def _get_tts():
    global _tts_model
    if _tts_model is None:
        from TTS.api import TTS
        os.environ["COQUI_TOS_AGREED"] = "1"
        print("Loading Coqui XTTS v2 model...")
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)
        print("Coqui ready.")
    return _tts_model


def _get_conditioning_latents():
    global _gpt_cond_latent, _speaker_embedding
    if _gpt_cond_latent is None:
        tts = _get_tts()
        print(f"Encoding voice sample: {VOICE_SAMPLE}")
        _gpt_cond_latent, _speaker_embedding = (
            tts.synthesizer.tts_model.get_conditioning_latents(audio_path=VOICE_SAMPLE)
        )
        print("Speaker embedding cached.")
    return _gpt_cond_latent, _speaker_embedding


_FRENCH = {"je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
           "le", "la", "les", "de", "du", "des", "un", "une", "et",
           "est", "sont", "avec", "pour", "dans", "sur", "par", "qui",
           "que", "mais", "ou", "donc", "car", "mon", "ma", "mes"}


def _detect_language(text: str) -> str:
    words = set(text.lower().split())
    return "fr" if len(words & _FRENCH) >= 2 else "en"


def _clean(text: str) -> str:
    text = re.sub(r'[*#_`]', '', text)
    text = re.sub(r'\.{2,}', ',', text)
    text = re.sub(r'(?<=[a-zA-ZÀ-ÿ])\.', ', ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _truncate(text: str) -> str:
    words = text.split()
    if len(words) <= MAX_WORDS:
        return text
    cut = " ".join(words[:MAX_WORDS])
    last_stop = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
    return cut[:last_stop + 1] if last_stop != -1 else cut


def _synthesize(text: str) -> bytes:
    text = _truncate(_clean(text))
    if not text:
        raise ValueError("TTS input is empty after cleaning.")
    tts = _get_tts()
    gpt_cond_latent, speaker_embedding = _get_conditioning_latents()
    out = tts.synthesizer.tts_model.inference(
        text=text,
        language=_detect_language(text),
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
    )
    from TTS.utils.audio.numpy_transforms import save_wav
    buf = io.BytesIO()
    save_wav(wav=out["wav"], path=buf, sample_rate=tts.synthesizer.output_sample_rate)
    return buf.getvalue()


class TTSRequest(BaseModel):
    question: str


@app.post("/tts")
def text_to_speech(request: TTSRequest):
    try:
        audio_bytes = _synthesize(request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
