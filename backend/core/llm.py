import os
from langchain_ollama import ChatOllama, OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

# LangSmith tracing — auto-instruments all LangChain/LangGraph calls
if os.getenv("LANGSMITH_TRACING") == "true":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"))
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "chaima-cv-agent")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


_llm_cache: dict[float, ChatOllama] = {}


def get_llm(temperature: float = 0.2) -> ChatOllama:
    """Return a cached Ollama chat model instance."""
    if temperature not in _llm_cache:
        _llm_cache[temperature] = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
        )
    return _llm_cache[temperature]


def get_embeddings() -> OllamaEmbeddings:
    """Return the local Ollama embeddings model used for the vector store."""
    return OllamaEmbeddings(
        model=OLLAMA_EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
