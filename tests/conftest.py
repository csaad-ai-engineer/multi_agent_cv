"""
conftest.py — shared pytest fixtures, fake env vars, and module stubs.

WHY WE STUB sys.modules:
Python executes import statements at module load time. When our source files do
  `from langchain.prompts import ChatPromptTemplate`
Python needs langchain installed — even if the test will mock it later.

The solution: insert fake (MagicMock) modules into sys.modules BEFORE any
source file is imported. Python then finds our fake module instead of the
real package, so no installation is needed at all.

This means the test suite runs 100% offline with zero LLM calls.
"""
import os
import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# 1. Fake environment variables — must be set before any source import
# ---------------------------------------------------------------------------
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://fake.openai.azure.com/")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "fake-api-key")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
os.environ.setdefault("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
os.environ.setdefault("LANGSMITH_TRACING", "false")


# ---------------------------------------------------------------------------
# 2. Stub all external packages that are not yet installed
#    Each entry becomes a real Python module object (MagicMock) in sys.modules.
#    Any attribute access on it (e.g. ChatPromptTemplate) returns another Mock.
# ---------------------------------------------------------------------------
_EXTERNAL_PACKAGES = [
    # LangChain
    "langchain",
    "langchain.prompts",
    "langchain.chains",
    "langchain.schema",
    "langchain_openai",
    "langchain_ollama",
    "langchain_community",
    "langchain_community.document_loaders",
    "langchain_community.vectorstores",
    "langchain.text_splitter",
    # LangGraph
    "langgraph",
    "langgraph.graph",
    # LangSmith
    "langsmith",
    # FAISS
    "faiss",
    # Whisper
    "whisper",
    # Tiktoken
    "tiktoken",
]

for _pkg in _EXTERNAL_PACKAGES:
    if _pkg not in sys.modules:
        sys.modules[_pkg] = MagicMock()

# Special case: langgraph.graph needs END to be a real string constant
# (used in graph.py as: graph.add_edge(node, END))
sys.modules["langgraph.graph"].END = "__end__"
sys.modules["langgraph.graph"].StateGraph = MagicMock()

# dotenv — may or may not be installed; stub it too
if "dotenv" not in sys.modules:
    sys.modules["dotenv"] = MagicMock()

# NOTE: python-multipart is a real, required dependency for FastAPI's file-upload
# endpoints (used by /voice/stt) — install it (it's in requirements.txt), don't stub it.
# Stubbing it breaks FastAPI's own multipart-availability check.


# ---------------------------------------------------------------------------
# 3. Shared test fixtures
# ---------------------------------------------------------------------------
import pytest  # noqa: E402 — must come after sys.modules setup


@pytest.fixture
def sample_question_fr():
    return "Quelles sont tes compétences techniques ?"


@pytest.fixture
def sample_question_en():
    return "Tell me about your experience."


@pytest.fixture
def fake_llm_answer():
    return "This is a mocked LLM answer."
