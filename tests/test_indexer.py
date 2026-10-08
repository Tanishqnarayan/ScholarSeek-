"""Tests for inverted index build, postings, save/load."""

import tempfile
import unittest
from pathlib import Path

from search_engine.indexer import InvertedIndex
from search_engine.loader import load_documents

DOCS = Path(__file__).resolve().parent.parent / "documents"


class TestIndexer(unittest.TestCase):
    def setUp(self):
        self.docs = load_documents(DOCS)
        self.idx = InvertedIndex()
        self.idx.build(self.docs)

    def test_stats(self):
        self.assertEqual(self.idx.doc_count, len(self.docs))
        self.assertGreater(len(self.idx), 100)

    def test_postings_no_duplicates(self):
        for term, ids in self.idx.index.items():
            self.assertIsInstance(ids, set)
        self.assertIn("python", self.idx.index)
        self.assertGreaterEqual(len(self.idx.postings("python")), 1)

    def test_doc_frequency(self):
        self.assertGreaterEqual(self.idx.doc_frequency("database"), 1)
        self.assertEqual(self.idx.doc_frequency("zzz-no-such-term"), 0)

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "index.json"
            self.idx.save(p)
            loaded = InvertedIndex.load(p)
            self.assertEqual(loaded.doc_count, self.idx.doc_count)
            self.assertEqual(loaded.postings("python"), self.idx.postings("python"))

    def test_missing_load_raises(self):
        with self.assertRaises(FileNotFoundError):
            InvertedIndex.load(Path("nope.json"))


if __name__ == "__main__":
    unittest.main()
