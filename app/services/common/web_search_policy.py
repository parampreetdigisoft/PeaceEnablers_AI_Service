"""Decide when chat should call OpenAI Web Search."""

from __future__ import annotations

import re

_PEM_ONLY = re.compile(
    r"\b(pem score|pillar (score|rating)|kpi|index score|pem assessment|"
    r"peace enablers matrix score)\b",
    re.I,
)
_CURRENT_INTEL = re.compile(
    r"\b(latest|current|recent|today|this week|this month|developments?|"
    r"conflict|war|risks?|humanitarian|security|crisis|escalat|"
    r"ceasefire|outbreak|situation|news|globally|worldwide)\b",
    re.I,
)
_NEEDS_SOURCE = re.compile(
    r"\b(when did|who (is|was|signed)|independence|source|according to|"
    r"what happened|cite)\b",
    re.I,
)


def question_needs_web_search(question: str, rag_context: str) -> bool:
    """
    Web Search is conditional:
    - PEM scores / KPIs / pillar ratings → RAG only
    - current conflict/risk/humanitarian or source-needed facts → search
    - empty RAG for a non-PEM question → search
    """
    q = question or ""
    if _PEM_ONLY.search(q) and not _CURRENT_INTEL.search(q):
        return False
    if _CURRENT_INTEL.search(q) or _NEEDS_SOURCE.search(q):
        return True
    if not (rag_context or "").strip():
        return True
    return False
