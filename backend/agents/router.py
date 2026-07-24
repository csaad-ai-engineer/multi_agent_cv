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
    r"\b(skill\w*|tech\w*|stack\w*|language\w*|framework\w*|tool\w*|python\w*|java\w*|react\w*|ml|ai|deep.?learn\w*|"
    r"machine.?learn\w*|nlp|llm\w*|pytorch|tensorflow|compétence\w*|technologie\w*|maîtrise\w*)\b",
    re.IGNORECASE,
)
_PROJECTS_RE = re.compile(
    r"\b(project\w*|projet\w*|réalisation\w*|built|creat\w*|develop\w*|github|portfolio\w*|work.?on\w*|travail\w*)\b",
    re.IGNORECASE,
)
_CONTACT_RE = re.compile(
    r"\b(contact\w*|email\w*|linkedin\w*|phone\w*|availab\w*|hire\w*|recrut\w*|reach\w*|joindre\w*|disponib\w*)\b",
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
