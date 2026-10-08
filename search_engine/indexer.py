"""Inverted index using dicts/sets (stdlib only). word -> {doc_ids}."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from .loader import Document
from .preprocessor import preprocess


class InvertedIndex:
    """Buildable, serializable inverted index with term frequencies."""

    def __init__(self):
        # token -> set(doc_id)
        self.index: dict = defaultdict(set)
        # doc_id -> Counter(token -> freq)
        self.doc_term_freqs: dict = {}
        # doc_id -> total indexed tokens
        self.doc_lengths: dict = {}
        # doc_id -> Document metadata
        self.documents: dict = {}

    def __len__(self):
        return len(self.index)

    def add_document(self, doc: Document) -> int:
        """Index one document. Returns number of unique tokens added."""
        tokens = preprocess(doc.content)
        freqs = Counter(tokens)
        self.documents[doc.doc_id] = doc
        self.doc_term_freqs[doc.doc_id] = dict(freqs)
        self.doc_lengths[doc.doc_id] = sum(freqs.values())
        added = 0
        for token in freqs:
            before = len(self.index[token])
            self.index[token].add(doc.doc_id)
            if len(self.index[token]) > before:
                added += 1
        return added

    def build(self, documents: list) -> dict:
        """Build index from an iterable of Documents. Returns stats dict."""
        total_tokens = 0
        for doc in documents:  # loop over documents
            self.add_document(doc)
            total_tokens += self.doc_lengths.get(doc.doc_id, 0)
        return {
            "documents": len(self.documents),
            "unique_terms": len(self.index),
            "total_tokens": total_tokens,
        }

    @property
    def doc_count(self) -> int:
        """Number of indexed documents."""
        return len(self.documents)

    def doc_frequency(self, term: str) -> int:
        """Number of documents containing term."""
        return len(self.index.get(term, set()))

    def postings(self, term: str) -> set:
        """Doc ids containing term (empty set if absent)."""
        return set(self.index.get(term, set()))

    # ---- persistence (JSON) ----
    def to_dict(self) -> dict:
        """Serialize to plain JSON-compatible dict."""
        return {
            "index": {term: sorted(ids) for term, ids in self.index.items()},
            "doc_term_freqs": self.doc_term_freqs,
            "doc_lengths": self.doc_lengths,
            "documents": {
                doc_id: {
                    "doc_id": d.doc_id,
                    "title": d.title,
                    "filename": d.filename,
                    "category": d.category,
                    "content": d.content,
                    "word_count": d.word_count,
                    "char_count": d.char_count,
                    "content_hash": d.content_hash,
                    "loaded_at": d.loaded_at,
                }
                for doc_id, d in self.documents.items()
            },
        }

    def save(self, path: Path) -> None:
        """Save index to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "InvertedIndex":
        """Load index from JSON file."""
        from .loader import Document as DocCls

        with open(Path(path), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        idx = cls()
        for term, ids in data.get("index", {}).items():
            idx.index[term] = set(ids)
        idx.doc_term_freqs = {k: dict(v) for k, v in data.get("doc_term_freqs", {}).items()}
        idx.doc_lengths = dict(data.get("doc_lengths", {}))
        for doc_id, d in data.get("documents", {}).items():
            idx.documents[doc_id] = DocCls(**d)
        return idx
