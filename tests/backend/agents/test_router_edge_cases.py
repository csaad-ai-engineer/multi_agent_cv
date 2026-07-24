"""
Edge case tests for backend/agents/router.py — pure keyword matching, no LLM.
"""
from backend.agents.router import route_question, AgentRoute


def test_router_falls_back_on_empty_question():
    assert route_question("") == AgentRoute.CV_RAG


def test_router_falls_back_on_whitespace_only_question():
    assert route_question("   ") == AgentRoute.CV_RAG


def test_router_routes_french_skills_question():
    assert route_question("Quelles sont tes compétences techniques ?") == AgentRoute.SKILLS


def test_router_routes_french_contact_question():
    assert route_question("Comment puis-je te contacter ?") == AgentRoute.CONTACT


def test_router_routes_french_projects_question():
    assert route_question("Parle-moi de tes projets.") == AgentRoute.PROJECTS


def test_router_falls_back_on_numeric_question():
    assert route_question("42") == AgentRoute.CV_RAG


def test_router_handles_very_long_question():
    long_question = "Tell me about yourself. " * 200
    assert route_question(long_question) == AgentRoute.CV_RAG


def test_router_matches_keyword_regardless_of_punctuation():
    assert route_question("skills???!!!") == AgentRoute.SKILLS


def test_router_does_not_match_substring_inside_unrelated_word():
    # "reach" is a contact keyword, but word-boundary matching must not fire
    # just because a longer unrelated word happens to contain it.
    assert route_question("I overreached my budget this month.") == AgentRoute.CV_RAG
