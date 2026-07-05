"""
Tests for backend/core/llm.py

What we test:
- get_llm() returns an AzureChatOpenAI instance with the right config
- get_embeddings() returns an AzureOpenAIEmbeddings instance

We mock the classes themselves so no network call is made.
"""
from unittest.mock import patch, MagicMock
from backend.core.llm import get_llm, get_embeddings


def test_get_llm_returns_azure_chat_instance():
    with patch("backend.core.llm.AzureChatOpenAI") as MockLLM:
        mock_instance = MagicMock()
        MockLLM.return_value = mock_instance

        result = get_llm()

        MockLLM.assert_called_once()
        assert result is mock_instance


def test_get_llm_uses_correct_deployment():
    with patch("backend.core.llm.AzureChatOpenAI") as MockLLM:
        get_llm()
        call_kwargs = MockLLM.call_args.kwargs
        assert call_kwargs["azure_deployment"] == "gpt-4o"


def test_get_llm_custom_temperature():
    with patch("backend.core.llm.AzureChatOpenAI") as MockLLM:
        get_llm(temperature=0.9)
        call_kwargs = MockLLM.call_args.kwargs
        assert call_kwargs["temperature"] == 0.9


def test_get_embeddings_returns_instance():
    with patch("backend.core.llm.AzureOpenAIEmbeddings") as MockEmbed:
        mock_instance = MagicMock()
        MockEmbed.return_value = mock_instance

        result = get_embeddings()

        MockEmbed.assert_called_once()
        assert result is mock_instance


def test_get_embeddings_uses_correct_deployment():
    with patch("backend.core.llm.AzureOpenAIEmbeddings") as MockEmbed:
        get_embeddings()
        call_kwargs = MockEmbed.call_args.kwargs
        assert call_kwargs["azure_deployment"] == "text-embedding-ada-002"
