"""
Tests for backend/agents/contact_agent.py
"""
from unittest.mock import patch, MagicMock


def _mock_chain(answer: str):
    mock_result = MagicMock()
    mock_result.content = answer
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_result
    return mock_chain


def test_answer_contact_question_returns_string():
    with patch("backend.agents.contact_agent.get_llm") as MockLLM:
        MockLLM.return_value.__or__ = MagicMock(return_value=_mock_chain("You can reach her at zidisaad.chaima@gmail.com"))

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("How can I contact Chaima?")

        assert isinstance(result, str)
        assert len(result) > 0


def test_answer_contact_question_passes_question():
    with patch("backend.agents.contact_agent.get_llm") as MockLLM:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = MagicMock(content="answer")
        MockLLM.return_value.__or__ = MagicMock(return_value=mock_chain)

        from backend.agents.contact_agent import answer_contact_question
        answer_contact_question("What is her email?")

        mock_chain.invoke.assert_called_once_with({"question": "What is her email?"})


def test_contact_info_contains_real_data():
    from backend.agents.contact_agent import CONTACT_INFO
    assert "zidisaad.chaima@gmail.com" in CONTACT_INFO
    assert "+33 758.949.591" in CONTACT_INFO
    assert "github.com/CSAADZIDI" in CONTACT_INFO
    assert "France" in CONTACT_INFO


def test_answer_contact_returns_llm_content():
    expected = "Her email is zidisaad.chaima@gmail.com."
    with patch("backend.agents.contact_agent.get_llm") as MockLLM:
        MockLLM.return_value.__or__ = MagicMock(return_value=_mock_chain(expected))

        from backend.agents.contact_agent import answer_contact_question
        result = answer_contact_question("Contact?")

        assert result == expected
