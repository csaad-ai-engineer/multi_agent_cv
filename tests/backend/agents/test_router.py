"""
Tests for backend/agents/router.py

What we test:
- route_question() returns the correct AgentRoute for each type of question
- Unknown/garbage LLM output falls back to cv_rag
- temperature=0 is used (deterministic routing)

The LLM chain is mocked so it returns a controlled string.
"""
from unittest.mock import patch, MagicMock
from backend.agents.router import route_question, AgentRoute


def _mock_llm_response(content: str):
    """Helper: create a fake LLM response with the given content string."""
    mock_result = MagicMock()
    mock_result.content = content
    return mock_result


def test_routes_to_skills():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("skills")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("What are your technical skills?")
        assert result == AgentRoute.SKILLS


def test_routes_to_projects():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("projects")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Tell me about your projects.")
        assert result == AgentRoute.PROJECTS


def test_routes_to_contact():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("contact")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("How can I contact you?")
        assert result == AgentRoute.CONTACT


def test_routes_to_cv_rag_for_general_questions():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("cv_rag")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Tell me about yourself.")
        assert result == AgentRoute.CV_RAG


def test_falls_back_to_cv_rag_on_unknown_output():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("something_unexpected")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("Some weird question")
        assert result == AgentRoute.CV_RAG


def test_router_uses_temperature_zero():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("cv_rag")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        route_question("Any question")
        MockLLM.assert_called_once_with(temperature=0)


def test_route_strips_whitespace_and_lowercases():
    with patch("backend.agents.router.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _mock_llm_response("  SKILLS  ")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = route_question("skills question")
        assert result == AgentRoute.SKILLS
