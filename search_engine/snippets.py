"""Snippet generation: short context window around first query-term hit."""

import re


def build_snippet(content: str, query_terms: list, phrases: list = None, window: int = 120) -> str:
    """Return a ~2*window char snippet preferably containing a query term.

    Falls back to the document start when nothing matches.
    """
    phrases = phrases or []
    if not content:
        return ""
    lowered = content.lower()
    best = -1
    # Prefer exact phrase position first.
    for phrase in phrases:  # loop over phrases
        pos = lowered.find(phrase.lower())
        if pos != -1 and (best == -1 or pos < best):
            best = pos
    # Otherwise earliest query-term occurrence.
    if best == -1:
        for term in query_terms:
            match = re.search(r"\b" + re.escape(term.lower()) + r"\b", lowered)
            if match and (best == -1 or match.start() < best):
                best = match.start()
    if best == -1:
        snippet = content[: window * 2].strip()
        return ("..." + snippet + "...") if len(content) > window * 2 else snippet

    start = max(0, best - window)
    end = min(len(content), best + window)
    snippet = content[start:end].strip()
    # Avoid cutting mid-word at the edges.
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    # Collapse whitespace for clean display.
    return re.sub(r"\s+", " ", snippet)


def highlight_snippet(snippet: str, query_terms: list) -> str:
    """Wrap matched terms in <mark> tags (HTML-escaped input assumed safe here)."""
    result = snippet
    for term in sorted(set(query_terms), key=len, reverse=True):  # longest first
        result = re.sub(
            r"(?i)\b(" + re.escape(term) + r")\b",
            r"<mark>\1</mark>",
            result,
        )
    return result
