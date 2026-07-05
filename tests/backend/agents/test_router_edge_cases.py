"""
Edge case and error handling tests for backend/agents/router.py

We patch ROUTER_PROMPT directly (instead of get_llm) because `ROUTER_PROMPT | llm`
calls __or__ on ROUTER_PROMPT, so patching the prompt gives reliable control over
what chain.invoke returns.
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.agents.router import route_question, AgentRoute


def _make_chain(response: str):
    mock_result = MagicMock()
    mock_result.content = response
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def test_router_raises_when_chain_raises():
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("LLM API timeout")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        with pytest.raises(Exception, match="LLM API timeout"):
            route_question("What are your skills?")


def test_router_falls_back_on_empty_llm_response():
    mock_chain = _make_chain("")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Any question")
        assert result == AgentRoute.CV_RAG


def test_router_falls_back_on_multiline_llm_response():
    # LLM returns extra text after the route word → not a valid enum value
    mock_chain = _make_chain("skills\nsome extra explanation")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("What frameworks do you use?")
        assert result == AgentRoute.CV_RAG


def test_router_routes_french_skills_question():
    mock_chain = _make_chain("skills")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Quelles sont tes compétences techniques ?")
        assert result == AgentRoute.SKILLS


def test_router_routes_french_contact_question():
    mock_chain = _make_chain("contact")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Comment puis-je te contacter ?")
        assert result == AgentRoute.CONTACT


def test_router_falls_back_on_numeric_llm_response():
    mock_chain = _make_chain("42")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("random question")
        assert result == AgentRoute.CV_RAG


def test_router_handles_very_long_question():
    long_question = "Tell me about yourself. " * 200
    mock_chain = _make_chain("cv_rag")

    with patch("backend.agents.router.ROUTER_PROMPT") as MockPrompt, \
         patch("backend.agents.router.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        result = route_question(long_question)

        assert result == AgentRoute.CV_RAG
        mock_chain.invoke.assert_called_once_with({"question": long_question})
