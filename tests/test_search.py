"""Tests for search, ranking, phrases, boolean ops, snippets, pagination."""

import unittest
from pathlib import Path

from search_engine.engine import SearchEngine
from search_engine.query_parser import parse_query
from search_engine.ranker import inverse_doc_frequency, term_frequency
from search_engine.snippets import build_snippet

DOCS = Path(__file__).resolve().parent.parent / "documents"


def make_engine():
    engine = SearchEngine(documents_dir=DOCS)
    engine.build_index(DOCS)
    return engine


class TestQueryParser(unittest.TestCase):
    def test_single_word(self):
        p = parse_query("python")
        self.assertIn("python", p.tokens)

    def test_case_insensitive(self):
        self.assertEqual(parse_query("Python").tokens, parse_query("python").tokens)

    def test_phrase(self):
        p = parse_query('"deadlock detection"')
        self.assertIn("deadlock detection", p.phrases)

    def test_boolean_and(self):
        p = parse_query("python AND django")
        self.assertEqual(p.operator, "AND")
        self.assertIn("python", p.must_terms)

    def test_boolean_not(self):
        p = parse_query("python NOT django")
        self.assertIn("django", p.not_terms)

    def test_empty(self):
        self.assertTrue(parse_query("   ").is_empty)
        self.assertTrue(parse_query("the and or").is_empty)

    def test_none_raises(self):
        with self.assertRaises(ValueError):
            parse_query(None)


class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = make_engine()

    def test_single_word_search(self):
        res = self.engine.search("python")
        self.assertGreater(len(res), 0)
        self.assertEqual(res[0]["filename"], "python.txt")

    def test_multi_term_ranking(self):
        res = self.engine.search("database normalization")
        files = [r["filename"] for r in res]
        self.assertIn("dbms.txt", files)
        self.assertEqual(files[0], "dbms.txt")
        scores = [r["relevance"] for r in res]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(scores[0], 100.0)

    def test_phrase_search(self):
        res = self.engine.search('"deadlock detection"')
        self.assertGreater(len(res), 0)
        self.assertEqual(res[0]["filename"], "os.txt")

    def test_boolean_and(self):
        res = self.engine.search("python AND django")
        self.assertGreater(len(res), 0)
        self.assertEqual(res[0]["filename"], "python.txt")

    def test_boolean_or(self):
        res = self.engine.search("python OR deadlock")
        files = {r["filename"] for r in res}
        self.assertIn("python.txt", files)
        self.assertIn("os.txt", files)

    def test_boolean_not(self):
        res = self.engine.search("python NOT django")
        files = [r["filename"] for r in res]
        self.assertNotIn("python.txt", files)

    def test_empty_query_returns_empty(self):
        self.assertEqual(self.engine.search(""), [])
        self.assertEqual(self.engine.search("the and or"), [])

    def test_snippet_contains_term(self):
        res = self.engine.search("database normalization")
        snippet = res[0]["snippet"].lower()
        self.assertTrue("database" in snippet or "normalization" in snippet)

    def test_snippet_fallback(self):
        s = build_snippet("hello world", ["zzz"])
        self.assertIn("hello", s)

    def test_pagination(self):
        res = self.engine.search("python")
        page = self.engine.paginate(res, page=1, per_page=1)
        self.assertEqual(len(page["items"]), 1)
        self.assertGreaterEqual(page["pages"], 1)

    def test_tf_idf_math(self):
        self.assertEqual(term_frequency(0), 0.0)
        self.assertGreater(term_frequency(5), term_frequency(1))
        self.assertGreater(inverse_doc_frequency(10, 1), inverse_doc_frequency(10, 9))


if __name__ == "__main__":
    unittest.main()
