"""Manual TF-IDF ranking (no sklearn, stdlib math only)."""

import math
from dataclasses import dataclass


@dataclass
class RankedResult:
    """Single ranked hit."""

    doc_id: str
    score: float          # raw tf-idf score
    relevance: float      # normalized 0-100 %
    matched_terms: list   # query tokens found in doc
    phrase_matched: bool = False

    def as_tuple(self):
        """Immutable (doc_id, relevance) pair."""
        return (self.doc_id, round(self.relevance, 1))


def term_frequency(freq: int) -> float:
    """Sublinear TF: 1 + log(freq), 0 when absent."""
    if freq <= 0:
        return 0.0
    return 1.0 + math.log(freq)


def inverse_doc_frequency(total_docs: int, doc_freq: int) -> float:
    """Smoothed IDF: log((1 + N) / (1 + df)) + 1, always >= 1."""
    if total_docs <= 0:
        return 0.0
    return math.log((1 + total_docs) / (1 + doc_freq)) + 1.0


def score_document(query_terms: list, doc_id: str, index) -> tuple:
    """Return (raw_score, matched_terms) for one document."""
    matched = []
    raw = 0.0
    total_docs = index.doc_count
    freqs = index.doc_term_freqs.get(doc_id, {})
    for term in query_terms:  # loop over query terms
        freq = freqs.get(term, 0)
        if freq > 0:
            matched.append(term)
            raw += term_frequency(freq) * inverse_doc_frequency(total_docs, index.doc_frequency(term))
    return raw, matched


def rank_documents(query_terms: list, candidate_ids: set, index, phrase_boost_docs: set = None) -> list:
    """Score candidates and return RankedResults sorted by relevance desc.

    Ranking considers TF, IDF, number of matching terms (coverage boost) and
    phrase matches (1.5x boost). Relevance is normalized to 0-100%.
    """
    phrase_boost_docs = phrase_boost_docs or set()
    scored = []
    for doc_id in candidate_ids:  # loop over candidates
        raw, matched = score_document(query_terms, doc_id, index)
        if not matched:
            continue
        coverage = len(matched) / max(len(query_terms), 1)
        raw *= 0.5 + coverage  # coverage boost in [0.5, 1.5]
        phrase_hit = doc_id in phrase_boost_docs
        if phrase_hit:
            raw *= 1.5
        scored.append(RankedResult(doc_id, raw, 0.0, matched, phrase_hit))

    if not scored:
        return []
    # Sort by raw score descending using a lambda (syllabus requirement).
    scored.sort(key=lambda r: r.score, reverse=True)
    top = scored[0].score if scored[0].score > 0 else 1.0
    for res in scored:
        res.relevance = round((res.score / top) * 100.0, 1)
    return scored
