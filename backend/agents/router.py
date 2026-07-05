"""
Router Agent — the brain of the multi-agent system.

Uses keyword matching instead of an LLM call to avoid doubling latency.
Falls back to cv_rag for anything that doesn't match a clear category.
"""
import re
from enum import Enum


class AgentRoute(str, Enum):
    CV_RAG = "cv_rag"
    SKILLS = "skills"
    PROJECTS = "projects"
    CONTACT = "contact"


_SKILLS_RE = re.compile(
    r"\b(skill|tech|stack|language|framework|tool|python|java|react|ml|ai|deep.?learn|"
    r"machine.?learn|nlp|llm|pytorch|tensorflow|compétence|technologie|maîtrise)\b",
    re.IGNORECASE,
)
_PROJECTS_RE = re.compile(
    r"\b(project|projet|réalisation|built|created|developed|github|portfolio|work.?on|travail)\b",
    re.IGNORECASE,
)
_CONTACT_RE = re.compile(
    r"\b(contact|email|linkedin|phone|available|availability|hire|recrut|reach|joindre|disponib)\b",
    re.IGNORECASE,
)


def route_question(question: str) -> AgentRoute:
    """Route by keyword matching — no LLM call needed."""
    if _CONTACT_RE.search(question):
        return AgentRoute.CONTACT
    if _PROJECTS_RE.search(question):
        return AgentRoute.PROJECTS
    if _SKILLS_RE.search(question):
        return AgentRoute.SKILLS
    return AgentRoute.CV_RAG
