"""
Tests for backend/agents/router.py

What we test:
- route_question() returns the correct AgentRoute for each type of question
- Ambiguous/general questions fall back to cv_rag
- Routing is pure keyword matching — no LLM call, so no mocking needed
"""
from backend.agents.router import route_question, AgentRoute


def test_routes_to_skills():
    assert route_question("What are your technical skills?") == AgentRoute.SKILLS


def test_routes_to_projects():
    assert route_question("Tell me about your projects.") == AgentRoute.PROJECTS


def test_routes_to_contact():
    assert route_question("How can I contact you?") == AgentRoute.CONTACT


def test_routes_to_cv_rag_for_general_questions():
    assert route_question("Tell me about yourself.") == AgentRoute.CV_RAG


def test_falls_back_to_cv_rag_when_no_keyword_matches():
    assert route_question("What do you enjoy doing on weekends?") == AgentRoute.CV_RAG


def test_route_is_case_insensitive():
    assert route_question("WHAT ARE YOUR SKILLS?") == AgentRoute.SKILLS


def test_contact_takes_priority_over_other_keywords():
    # Router checks contact first — a question mentioning both project work
    # and contact info should still route to contact.
    question = "Can I contact you about a project opportunity?"
    assert route_question(question) == AgentRoute.CONTACT
