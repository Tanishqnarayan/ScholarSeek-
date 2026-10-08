"""Query parsing: phrases, boolean AND/OR/NOT, case-insensitive (stdlib only)."""

import re
from dataclasses import dataclass, field

from .preprocessor import preprocess

_PHRASE_RE = re.compile(r'"([^"]+)"')


@dataclass
class ParsedQuery:
    """Structured representation of a raw query string."""

    raw: str
    phrases: list = field(default_factory=list)      # exact phrase strings (lowercased)
    must_terms: list = field(default_factory=list)   # AND group tokens
    should_terms: list = field(default_factory=list)  # OR group tokens
    not_terms: list = field(default_factory=list)    # NOT tokens
    operator: str = "OR"                             # default combination
    tokens: list = field(default_factory=list)       # all positive tokens

    @property
    def is_empty(self) -> bool:
        """True when no searchable tokens or phrases remain."""
        return not self.tokens and not self.phrases


def parse_query(raw: str) -> ParsedQuery:
    """Parse raw query into a ParsedQuery.

    Supports:
      - "exact phrases" in double quotes
      - python AND django / python OR java / python NOT django (case-insensitive)
      - plain multi-term queries (default OR semantics, ranked by coverage)
    """
    if raw is None:
        raise ValueError("Query must be a string, got None")
    if not isinstance(raw, str):
        raise ValueError("Query must be a string")
    text = raw.strip()
    parsed = ParsedQuery(raw=raw)
    if not text:
        return parsed

    # 1. Extract exact phrases first.
    phrases = _PHRASE_RE.findall(text)
    parsed.phrases = [p.lower().strip() for p in phrases if p.strip()]
    text_wo_phrases = _PHRASE_RE.sub(" ", text)

    # 2. Detect boolean operators (word-boundary, case-insensitive).
    upper = f" {text_wo_phrases.upper()} "
    has_and = " AND " in upper
    has_or = " OR " in upper
    has_not = " NOT " in upper

    if has_and:
        parsed.operator = "AND"
    elif has_or:
        parsed.operator = "OR"

    # 3. Split on operators to obtain groups; NOT xxx always goes to not_terms.
    # Tokenize each segment with the same pipeline as documents.
    not_parts = re.split(r"\bNOT\b", text_wo_phrases, flags=re.IGNORECASE)
    positive_part = not_parts[0]
    for neg in not_parts[1:]:
        parsed.not_terms.extend(preprocess(neg))

    if has_and and not has_or:
        for segment in re.split(r"\bAND\b", positive_part, flags=re.IGNORECASE):
            parsed.must_terms.extend(preprocess(segment))
        parsed.tokens = list(parsed.must_terms)
    elif has_or and not has_and:
        for segment in re.split(r"\bOR\b", positive_part, flags=re.IGNORECASE):
            parsed.should_terms.extend(preprocess(segment))
        parsed.tokens = list(parsed.should_terms)
    else:
        # Mixed or plain query: treat AND-segments as must, rest as should.
        if has_and:
            for segment in re.split(r"\bAND\b", positive_part, flags=re.IGNORECASE):
                parsed.must_terms.extend(preprocess(segment))
        parsed.should_terms.extend(preprocess(re.sub(r"\bAND\b|\bOR\b", " ", positive_part, flags=re.IGNORECASE)))
        parsed.tokens = list(dict.fromkeys(parsed.must_terms + parsed.should_terms))

    # 4. Phrase tokens also contribute to ranking/snippet matching.
    for phrase in parsed.phrases:
        for tok in preprocess(phrase):
            if tok not in parsed.tokens:
                parsed.tokens.append(tok)
    return parsed
