"""
FastAPI server — exposes the multi-agent graph as HTTP endpoints.

Endpoints:
  POST /chat        → text question → text answer
  POST /voice/stt   → audio file → transcribed text
  POST /voice/tts   → text → audio (Coqui XTTS v2 cloned voice)
  GET  /health      → server status check
"""
import io
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.core.graph import cv_agent_graph
from backend.core.safety import looks_like_injection, enforce_answer_limits, REFUSAL_MESSAGE
from backend.voice.stt import transcribe_audio
from backend.voice.tts import synthesize_speech


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.agents.cv_rag_agent import get_cv_rag_chain
    from backend.core.llm import get_llm
    get_cv_rag_chain()      # load vectorstore + build chain
    get_llm().invoke("hi")  # pull LLM into Ollama memory
    yield


app = FastAPI(title="Chaima SAAD — CV Agent API", lifespan=lifespan)

# Rate limiting — protects the (self-hosted) LLM/voice services from abuse.
# Keyed by client IP since this is an unauthenticated public API.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow the React frontend to call this API.
# Configure via ALLOWED_ORIGINS (comma-separated) in production; defaults cover local dev.
_default_origins = "http://localhost:5173,http://localhost:80,http://localhost"
allowed_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    route: str = ""  # which agent handled it (useful for debugging)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("15/minute")
def chat(request: Request, chat_request: ChatRequest):
    """Main text chat endpoint used by the frontend."""
    if looks_like_injection(chat_request.question):
        return ChatResponse(answer=REFUSAL_MESSAGE, route="refused")

    result = cv_agent_graph.invoke({"question": chat_request.question})
    answer = enforce_answer_limits(result["answer"])
    return ChatResponse(answer=answer, route=result.get("route", ""))


@app.post("/voice/stt")
@limiter.limit("15/minute")
async def speech_to_text(request: Request, audio: UploadFile = File(...)):
    """Convert uploaded audio to text using Whisper."""
    audio_bytes = await audio.read()
    text = transcribe_audio(audio_bytes)
    return {"text": text}


@app.post("/voice/tts")
@limiter.limit("15/minute")
async def text_to_speech(request: Request, chat_request: ChatRequest):
    """Convert text to audio using Coqui XTTS v2 (local voice cloning)."""
    from fastapi.responses import StreamingResponse
    try:
        audio_bytes = synthesize_speech(chat_request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
