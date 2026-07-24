"""
Tests for backend/core/llm.py

What we test:
- get_llm() returns a ChatOllama instance with the right config, cached per temperature
- get_embeddings() returns an OllamaEmbeddings instance

We mock the classes themselves so no network call is made.

WHY WE RESET _llm_cache BEFORE EACH TEST:
get_llm() caches instances per temperature in a module-level dict so
production code reuses connections. Tests must reset it first or a
cached instance from an earlier test leaks in instead of the new mock.
"""
import pytest
from unittest.mock import patch, MagicMock

import backend.core.llm as llm_module


@pytest.fixture(autouse=True)
def _reset_llm_cache():
    llm_module._llm_cache.clear()
    yield
    llm_module._llm_cache.clear()


def test_get_llm_returns_chat_ollama_instance():
    with patch("backend.core.llm.ChatOllama") as MockLLM:
        mock_instance = MagicMock()
        MockLLM.return_value = mock_instance

        result = llm_module.get_llm()

        MockLLM.assert_called_once()
        assert result is mock_instance


def test_get_llm_uses_correct_model():
    with patch("backend.core.llm.ChatOllama") as MockLLM:
        llm_module.get_llm()
        call_kwargs = MockLLM.call_args.kwargs
        assert call_kwargs["model"] == llm_module.OLLAMA_MODEL


def test_get_llm_custom_temperature():
    with patch("backend.core.llm.ChatOllama") as MockLLM:
        llm_module.get_llm(temperature=0.9)
        call_kwargs = MockLLM.call_args.kwargs
        assert call_kwargs["temperature"] == 0.9


def test_get_llm_caches_instance_per_temperature():
    with patch("backend.core.llm.ChatOllama") as MockLLM:
        MockLLM.side_effect = lambda **kwargs: MagicMock()

        first = llm_module.get_llm(temperature=0.5)
        second = llm_module.get_llm(temperature=0.5)

        assert first is second
        MockLLM.assert_called_once()


def test_get_embeddings_returns_instance():
    with patch("backend.core.llm.OllamaEmbeddings") as MockEmbed:
        mock_instance = MagicMock()
        MockEmbed.return_value = mock_instance

        result = llm_module.get_embeddings()

        MockEmbed.assert_called_once()
        assert result is mock_instance


def test_get_embeddings_uses_correct_model():
    with patch("backend.core.llm.OllamaEmbeddings") as MockEmbed:
        llm_module.get_embeddings()
        call_kwargs = MockEmbed.call_args.kwargs
        assert call_kwargs["model"] == llm_module.OLLAMA_EMBEDDING_MODEL
