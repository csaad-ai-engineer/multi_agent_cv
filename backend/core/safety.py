"""
Safety guards for the chat pipeline: prompt-injection detection and output enforcement.

These are lightweight, deterministic checks — not a substitute for careful
prompting, but a cheap first line of defense against obvious attempts to
override the assistant's role or exfiltrate its system prompt. A determined
attacker who rephrases carefully can still get past keyword matching; treat
this as one layer, not a guarantee.
"""
import re

_INJECTION_RE = re.compile(
    r"\b(ignore|disregard|forget)\b.{0,40}\b(previous|prior|above|earlier)\b.{0,20}\b(instruction|prompt|rule)|"
    r"\bsystem\s*prompt\b|"
    r"\byou\s+are\s+now\b|"
    r"\bact\s+as\s+(a|an)\b|"
    r"\breveal\s+(your|the)\s+(instruction|prompt|system)|"
    r"\bnew\s+instructions?\b|"
    r"\bprint\s+(your|the)\s+(instructions?|prompt|rules?)\b|"
    r"\brepeat\s+(the\s+words?\s+above|your\s+(instructions?|prompt))\b|"
    # French equivalents — the assistant is explicitly bilingual (FR/EN)
    r"\bignor[ez]\b.{0,40}\b(instructions?|consignes?|r[eè]gles?)\b|"
    r"\bprompt\s+syst[eè]me\b|"
    r"\btu\s+es\s+maintenant\b|"
    r"\bagis\s+comme\b|"
    r"\bmontre[- ]moi\s+(tes|ton)\s+(instructions?|prompt|consignes?)\b|"
    r"\bnouvelles?\s+instructions?\b",
    re.IGNORECASE,
)

REFUSAL_MESSAGE = (
    "I can only answer questions about Chaima's profile, skills, projects, and contact details — "
    "I'm not able to follow instructions embedded in a question."
)

# Phrases that only exist in our system prompts — if one shows up in a generated
# answer, the model is very likely leaking its instructions rather than answering.
_LEAK_MARKERS = (
    "you are chaima saad speaking",
    "use only the information in the context",
    "untrusted user input, not instructions",
    "never use bullet points, lists, or headers",
    "keep answers to 2 sentences maximum",
)

MAX_ANSWER_CHARS = 800
MAX_SENTENCES = 3  # one more than the prompt's target, to allow for natural phrasing


def looks_like_injection(question: str) -> bool:
    """Cheap keyword/pattern check for obvious prompt-injection attempts."""
    return bool(_INJECTION_RE.search(question))


def looks_like_leak(answer: str) -> bool:
    """Detect an answer that echoes back system-prompt language instead of Chaima's content."""
    lowered = answer.lower()
    return any(marker in lowered for marker in _LEAK_MARKERS)


def _limit_sentences(answer: str, max_sentences: int) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", answer)
    if len(sentences) <= max_sentences:
        return answer
    return " ".join(sentences[:max_sentences])


def enforce_answer_limits(answer: str, max_chars: int = MAX_ANSWER_CHARS) -> str:
    """Safety-net cleanup in case the LLM ignores the prompt's constraints or leaks it."""
    answer = answer.strip()

    if looks_like_leak(answer):
        return REFUSAL_MESSAGE

    answer = _limit_sentences(answer, MAX_SENTENCES)

    if len(answer) <= max_chars:
        return answer
    truncated = answer[:max_chars]
    last_stop = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
    return truncated[: last_stop + 1] if last_stop != -1 else truncated
