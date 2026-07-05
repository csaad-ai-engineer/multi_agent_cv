"""
Tests for backend/agents/projects_agent.py
"""
from unittest.mock import patch, MagicMock


def _make_chain(answer: str):
    mock_result = MagicMock()
    mock_result.content = answer
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def test_answer_projects_question_returns_string():
    mock_chain = _make_chain("She built a RAG agent.")
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        result = answer_projects_question("What projects has she done?")

        assert isinstance(result, str)
        assert result == "She built a RAG agent."


def test_answer_projects_question_passes_question():
    mock_chain = _make_chain("answer")
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        answer_projects_question("Tell me about her LangGraph project.")

        mock_chain.invoke.assert_called_once_with({"question": "Tell me about her LangGraph project."})


def test_projects_data_contains_key_projects():
    from backend.agents.projects_agent import CHAIMA_PROJECTS
    assert "RAG" in CHAIMA_PROJECTS
    assert "LangGraph" in CHAIMA_PROJECTS
    assert "LangChain" in CHAIMA_PROJECTS
    assert "IMT Nord Europe" in CHAIMA_PROJECTS


def test_answer_projects_returns_llm_content():
    expected = "She built a multi-agent system with LangGraph."
    mock_chain = _make_chain(expected)
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        result = answer_projects_question("Projects?")

        assert result == expected
