"""
Tests for backend/agents/contact_agent.py

WHY WE PATCH THE PROMPT DIRECTLY:
The source code does: `chain = CONTACT_PROMPT | llm`
Because ChatPromptTemplate is stubbed, CONTACT_PROMPT is already a MagicMock
at import time, and MagicMock defines its own `__or__`. Patching `get_llm`
alone doesn't control the result of `CONTACT_PROMPT | llm` — we must patch
CONTACT_PROMPT itself so we control what `.invoke()` returns.
"""
from unittest.mock import patch, MagicMock


def _make_chain(answer: str):
    mock_result = MagicMock()
    mock_result.content = answer
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def test_answer_contact_question_returns_string():
    mock_chain = _make_chain("You can reach her at chaima.zidi.ingia@gmail.com")
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("How can I contact Chaima?")

        assert isinstance(result, str)
        assert len(result) > 0


def test_answer_contact_question_passes_question():
    mock_chain = _make_chain("answer")
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        answer_contact_question("What is her email?")

        mock_chain.invoke.assert_called_once_with({"question": "What is her email?"})


def test_contact_info_contains_real_data():
    from backend.agents.contact_agent import CONTACT_INFO
    assert "chaima.zidi.ingia@gmail.com" in CONTACT_INFO
    assert "+33 758.949.591" in CONTACT_INFO
    assert "github.com/csaad-ai-engineer" in CONTACT_INFO
    assert "France" in CONTACT_INFO


def test_answer_contact_returns_llm_content():
    expected = "Her email is chaima.zidi.ingia@gmail.com."
    mock_chain = _make_chain(expected)
    with patch("backend.agents.contact_agent.CONTACT_PROMPT") as MockPrompt, \
         patch("backend.agents.contact_agent.get_llm"):
        MockPrompt.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("Contact?")

        assert result == expected
