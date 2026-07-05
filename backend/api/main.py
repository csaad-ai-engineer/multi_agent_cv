"""
FastAPI server — exposes the multi-agent graph as HTTP endpoints.

Endpoints:
  POST /chat        → text question → text answer
  POST /voice/stt   → audio file → transcribed text
  POST /voice/tts   → text → audio (ElevenLabs cloned voice)
  GET  /health      → server status check
"""
import io
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.core.graph import ask
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

# Allow the React frontend (on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your domain in production
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
def chat(request: ChatRequest):
    """Main text chat endpoint used by the frontend."""
    from backend.core.graph import cv_agent_graph
    result = cv_agent_graph.invoke({"question": request.question})
    return ChatResponse(answer=result["answer"], route=result.get("route", ""))


@app.post("/voice/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert uploaded audio to text using Whisper."""
    audio_bytes = await audio.read()
    text = transcribe_audio(audio_bytes)
    return {"text": text}


@app.post("/voice/tts")
async def text_to_speech(request: ChatRequest):
    """Convert text to audio using Coqui XTTS v2 (local voice cloning)."""
    from fastapi.responses import StreamingResponse
    try:
        audio_bytes = synthesize_speech(request.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")
