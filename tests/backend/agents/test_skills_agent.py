"""
Tests for backend/agents/skills_agent.py

WHY WE PATCH THE PROMPT DIRECTLY:
The source code does: `chain = SKILLS_PROMPT | llm`
Because ChatPromptTemplate is stubbed, SKILLS_PROMPT is already a MagicMock
at import time. We must patch that module-level variable so we control what
`SKILLS_PROMPT | llm` returns and what `.invoke()` gives back.
"""
from unittest.mock import patch, MagicMock


def _make_chain(answer: str):
    """Build a fake chain whose .invoke() returns an object with .content = answer."""
    mock_result = MagicMock()
    mock_result.content = answer
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def test_answer_skills_question_returns_string():
    mock_chain = _make_chain("Chaima knows LangGraph and FastAPI.")
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        result = answer_skills_question("What are her technical skills?")

        assert isinstance(result, str)
        assert result == "Chaima knows LangGraph and FastAPI."


def test_answer_skills_question_passes_question_to_chain():
    mock_chain = _make_chain("answer")
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        answer_skills_question("Does she know Docker?")

        mock_chain.invoke.assert_called_once_with({"question": "Does she know Docker?"})


def test_skills_prompt_contains_chaima_skills():
    from backend.agents.skills_agent import CHAIMA_SKILLS
    assert "LangGraph" in CHAIMA_SKILLS
    assert "FastAPI" in CHAIMA_SKILLS
    assert "Azure" in CHAIMA_SKILLS
    assert "Docker" in CHAIMA_SKILLS
    assert "RAG" in CHAIMA_SKILLS


def test_answer_skills_question_returns_llm_content():
    expected = "She is expert in LangChain and MLOps."
    mock_chain = _make_chain(expected)
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        result = answer_skills_question("Skills?")

        assert result == expected
