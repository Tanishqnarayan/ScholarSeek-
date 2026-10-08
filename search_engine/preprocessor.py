"""Text preprocessing pipeline (no NLP libraries, stdlib only)."""

import re
import string

# Configurable stop-word collection (Python set for O(1) lookup).
STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "not", "but", "if", "then", "else", "when", "while",
    "of", "at", "by", "for", "with", "about", "into", "through", "during",
    "to", "from", "in", "on", "as", "it", "its", "this", "that", "these",
    "those", "i", "you", "he", "she", "we", "they", "them", "his", "her",
    "our", "your", "their", "has", "have", "had", "do", "does", "did",
    "will", "would", "can", "could", "should", "may", "might", "must",
    "so", "such", "no", "nor", "too", "very", "just", "also", "than",
    "which", "who", "whom", "what", "where", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "only", "own", "same",
    "s", "t",
})

_PUNCT_TABLE = str.maketrans({ch: " " for ch in string.punctuation})
_WS_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize(text: str) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    if not isinstance(text, str):
        raise ValueError("normalize() expects a string")
    text = text.lower().translate(_PUNCT_TABLE)
    return _WS_RE.sub(" ", text).strip()


def tokenize(text: str) -> list:
    """Split normalized text into alphanumeric tokens."""
    normalized = normalize(text)
    return _TOKEN_RE.findall(normalized)


def remove_stopwords(tokens: list, stop_words=frozenset(STOP_WORDS)) -> list:
    """Filter stop words and invalid/empty tokens."""
    return [t for t in tokens if t and t not in stop_words and len(t) > 1]


def preprocess(text: str, stop_words=frozenset(STOP_WORDS)) -> list:
    """Full pipeline: normalize -> tokenize -> stop-word filter.

    Example:
        "Python is a high-level programming language."
        -> ["python", "high", "level", "programming", "language"]
    """
    if text is None:
        raise ValueError("preprocess() received None")
    if not isinstance(text, str):
        raise ValueError("preprocess() expects a string")
    tokens = tokenize(text)
    return remove_stopwords(tokens, stop_words)
