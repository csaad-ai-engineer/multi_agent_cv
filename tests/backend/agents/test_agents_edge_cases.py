"""
Edge case and error handling tests for skills, projects, and contact agents.
"""
import pytest
from unittest.mock import patch, MagicMock


def _make_chain(answer: str):
    mock_result = MagicMock()
    mock_result.content = answer
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def _make_failing_chain(error: Exception):
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = error
    return mock_chain


# --------------------------------------------------------------------------
# skills_agent edge cases
# --------------------------------------------------------------------------

def test_skills_agent_raises_on_llm_failure():
    mock_chain = _make_failing_chain(Exception("LLM unavailable"))
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        with pytest.raises(Exception, match="LLM unavailable"):
            answer_skills_question("What are your skills?")


def test_skills_agent_handles_empty_question():
    mock_chain = _make_chain("Please ask a specific question.")
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        result = answer_skills_question("")

        assert isinstance(result, str)
        mock_chain.invoke.assert_called_once_with({"question": ""})


def test_skills_agent_handles_french_question():
    mock_chain = _make_chain("Elle maîtrise LangGraph, FastAPI et TensorFlow.")
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        result = answer_skills_question("Quelles sont tes compétences ?")

        assert result == "Elle maîtrise LangGraph, FastAPI et TensorFlow."


def test_skills_agent_handles_very_long_question():
    long_q = "Tell me everything about your skills " * 100
    mock_chain = _make_chain("She has many skills.")
    with patch("backend.agents.skills_agent.SKILLS_PROMPT") as MockPrompt, \
         patch("backend.agents.skills_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.skills_agent import answer_skills_question
        result = answer_skills_question(long_q)

        assert result == "She has many skills."
        mock_chain.invoke.assert_called_once_with({"question": long_q})


# --------------------------------------------------------------------------
# projects_agent edge cases
# --------------------------------------------------------------------------

def test_projects_agent_raises_on_llm_failure():
    mock_chain = _make_failing_chain(Exception("LLM timeout"))
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        with pytest.raises(Exception, match="LLM timeout"):
            answer_projects_question("Tell me about your projects.")


def test_projects_agent_handles_empty_question():
    mock_chain = _make_chain("What would you like to know about my projects?")
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        result = answer_projects_question("")

        assert isinstance(result, str)
        mock_chain.invoke.assert_called_once_with({"question": ""})


def test_projects_agent_handles_french_question():
    mock_chain = _make_chain("Elle a développé un agent multi-modal.")
    with patch("backend.agents.projects_agent.PROJECTS_PROMPT") as MockPrompt, \
         patch("backend.agents.projects_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.projects_agent import answer_projects_question
        result = answer_projects_question("Parle-moi de tes projets.")

        assert result == "Elle a développé un agent multi-modal."


# --------------------------------------------------------------------------
# contact_agent edge cases
# --------------------------------------------------------------------------

def test_contact_agent_raises_on_llm_failure():
    mock_chain = _make_failing_chain(Exception("LLM connection refused"))
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        with pytest.raises(Exception, match="LLM connection refused"):
            answer_contact_question("How can I contact you?")


def test_contact_agent_handles_empty_question():
    mock_chain = _make_chain("You can reach me by email.")
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("")

        assert isinstance(result, str)
        mock_chain.invoke.assert_called_once_with({"question": ""})


def test_contact_agent_handles_french_question():
    mock_chain = _make_chain("Vous pouvez me contacter par email.")
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("Comment te contacter ?")

        assert result == "Vous pouvez me contacter par email."
