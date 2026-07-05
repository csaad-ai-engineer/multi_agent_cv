# multi-agent-cv

An AI-powered interactive CV assistant for **Chaima Saad**, built with LangGraph. Ask questions about her profile in natural language — by text or voice — and get answers from a multi-agent system backed by a local LLM and RAG over her CV.

---

## How it works

Every incoming question flows through a LangGraph pipeline:

```
User question
     │
     ▼
  Router (keyword matching)
     │
     ├── Skills questions    → Skills Agent    (structured skills data + LLM)
     ├── Project questions   → Projects Agent  (project data + LLM)
     ├── Contact questions   → Contact Agent   (contact info + LLM)
     └── Everything else     → CV RAG Agent    (FAISS vectorstore over CV PDF)
```

All agents respond in conversational prose (no bullet points), in the same language as the question (French or English).

Voice is fully supported:
- **STT** — OpenAI Whisper transcribes audio from the browser
- **TTS** — Coqui XTTS v2 synthesizes responses in Chaima's cloned voice

---

## Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM | Ollama (`llama3.1:8b`, local) |
| Embeddings | Ollama (`nomic-embed-text`, local) |
| Vector store | FAISS |
| Backend API | FastAPI |
| STT | OpenAI Whisper (`base`) |
| TTS | Coqui XTTS v2 (voice cloning) |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Containerization | Docker Compose |
| Tracing | LangSmith (optional) |

---

## Project structure

```
multi-agent-cv/
├── backend/
│   ├── agents/          # Router + 4 specialist agents
│   ├── api/             # FastAPI app (chat, STT, TTS, health endpoints)
│   ├── core/            # LangGraph graph, LLM config, FAISS vectorstore
│   └── voice/           # STT/TTS HTTP clients (proxy to voice service)
├── services/
│   └── voice_service.py # Host-side Whisper + Coqui service (port 8002)
├── frontend/
│   └── src/
│       ├── pages/       # Portfolio page + Persona (AI chat) page
│       └── components/  # Hero, Skills, Projects, Contact, ChatWidget
├── raw_data/            # CV PDF and text used to build the vectorstore
├── voice_data/          # Voice sample for XTTS cloning
├── tests/               # Full pytest suite (agents, API, core, voice)
└── docker-compose.yml
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) with the following models pulled:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

- Python 3.12+ (for the host-side voice service)

---

## Running locally

**1. Install voice service dependencies**

```bash
python3 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
```

**2. Start the voice service on the host** (needed for MPS/GPU access)

```bash
python services/voice_service.py
```

This starts Whisper (STT) and Coqui XTTS v2 (TTS) on port `8002`.

**3. Configure environment**

Copy `.env.azure` or create a `.env` file:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
VOICE_SAMPLE_PATH=/app/voice_data/voice_sample.mp3
```

**4. Start the backend and frontend**

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:80 |
| Backend API | http://localhost:8001 |
| API docs | http://localhost:8001/docs |
| Voice service | http://localhost:8002 |

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Server status |
| `POST` | `/chat` | Text question → text answer |
| `POST` | `/voice/stt` | Audio file → transcribed text |
| `POST` | `/voice/tts` | Text → WAV audio (cloned voice) |

**Example:**

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your main skills?"}'
```

```json
{
  "answer": "I have a strong background in generative and agentic AI...",
  "route": "cv_rag"
}
```

---

## Running tests

```bash
source .venv312/bin/activate
pytest tests/
```

---

## Notes

- The voice service runs on the **host machine** (not inside Docker) to access Apple MPS or CUDA. The backend container reaches it via `host.docker.internal:8002`.
- The FAISS index is built automatically on first startup from the CV PDF in `raw_data/`. Subsequent starts reuse the cached index.
- TTS responses are truncated to 60 words to keep synthesis fast. Language (French/English) is auto-detected.
- `.env` is intentionally excluded from version control — never commit secrets.

---

## Author

**Chaima Saad** — AI & Data Engineer  
chaima.zidi.ingia@gmail.com · [GitHub](https://github.com/csaad-ai-engineer)
