"""SearchEngine facade: indexing + query processing + ranking + snippets."""

from pathlib import Path

from .indexer import InvertedIndex
from .loader import load_documents
from .query_parser import parse_query
from .ranker import rank_documents
from .snippets import build_snippet


class SearchEngine:
    """High-level search API used by CLI and Django views."""

    def __init__(self, documents_dir: Path = None, index_path: Path = None):
        self.documents_dir = Path(documents_dir) if documents_dir else None
        self.index_path = Path(index_path) if index_path else None
        self.index = InvertedIndex()

    # ---- indexing ----
    def build_index(self, documents_dir: Path = None) -> dict:
        """Load documents and (re)build the inverted index."""
        directory = Path(documents_dir) if documents_dir else self.documents_dir
        if directory is None:
            raise ValueError("No documents directory provided")
        docs = load_documents(directory)
        if not docs:
            raise ValueError(f"No valid .txt documents found in {directory}")
        self.index = InvertedIndex()
        stats = self.index.build(docs)
        self.documents_dir = directory
        if self.index_path:
            self.index.save(self.index_path)
        return stats

    def load_index(self, path: Path = None) -> None:
        """Load a persisted JSON index."""
        target = Path(path) if path else self.index_path
        if target is None or not target.exists():
            raise FileNotFoundError(f"Index file not found: {target}")
        self.index = InvertedIndex.load(target)

    def save_index(self, path: Path = None) -> None:
        """Persist the current index to JSON."""
        target = Path(path) if path else self.index_path
        if target is None:
            raise ValueError("No index path provided")
        self.index.save(target)

    # ---- searching ----
    def search(self, query: str, top_k: int = 10) -> list:
        """Run a query and return ranked result dicts (highest relevance first).

        Each dict: doc_id, title, filename, category, relevance,
        matched_terms, snippet, phrase_matched.
        """
        parsed = parse_query(query)
        if parsed.is_empty or self.index.doc_count == 0:
            return []

        # Candidate retrieval via inverted index postings.
        candidates: set = set()
        if parsed.must_terms:
            must_sets = [self.index.postings(t) for t in parsed.must_terms]
            candidates = set.intersection(*must_sets) if must_sets else set()
            # AND semantics: doc must contain every must_term.
        elif parsed.should_terms or parsed.tokens:
            for term in (parsed.should_terms or parsed.tokens):
                candidates |= self.index.postings(term)
        # Phrase-only queries: scan all docs for the phrase.
        if not candidates and parsed.phrases:
            candidates = set(self.index.documents.keys())

        # Boolean NOT exclusion.
        for term in parsed.not_terms:
            candidates -= self.index.postings(term)

        # Phrase filtering/boost: docs whose raw text contains the phrase.
        phrase_docs = set()
        if parsed.phrases:
            for doc_id in list(candidates) or list(self.index.documents.keys()):
                text = self.index.documents[doc_id].content.lower()
                if any(p in text for p in parsed.phrases):
                    phrase_docs.add(doc_id)
            # If query is ONLY a phrase, restrict to phrase holders.
            if not parsed.tokens:
                candidates = set(phrase_docs)
            else:
                candidates |= phrase_docs

        ranked = rank_documents(parsed.tokens, candidates, self.index, phrase_docs)

        results = []  # list of result dicts
        for hit in ranked[: max(top_k, 1)]:
            doc = self.index.documents[hit.doc_id]
            results.append({
                "doc_id": hit.doc_id,
                "title": doc.title,
                "filename": doc.filename,
                "category": doc.category,
                "relevance": hit.relevance,
                "matched_terms": hit.matched_terms,
                "matched_count": len(hit.matched_terms),
                "phrase_matched": hit.phrase_matched,
                "snippet": build_snippet(doc.content, parsed.tokens, parsed.phrases),
                "word_count": doc.word_count,
            })
        return results

    def paginate(self, results: list, page: int = 1, per_page: int = 5) -> dict:
        """Simple pagination helper returning slice + metadata."""
        per_page = max(1, per_page)
        total = len(results)
        pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, pages))
        start = (page - 1) * per_page
        return {
            "items": results[start: start + per_page],
            "page": page,
            "pages": pages,
            "total": total,
            "per_page": per_page,
            "has_prev": page > 1,
            "has_next": page < pages,
        }
