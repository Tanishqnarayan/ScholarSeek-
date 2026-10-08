"""Tests for document loading, validation and edge cases."""

import tempfile
import unittest
from pathlib import Path

from search_engine.loader import DocumentError, iter_documents, load_document, load_documents

DOCS = Path(__file__).resolve().parent.parent / "documents"


class TestLoader(unittest.TestCase):
    def test_load_real_doc(self):
        doc = load_document(DOCS / "python.txt")
        self.assertEqual(doc.filename, "python.txt")
        self.assertTrue(doc.word_count > 50)
        self.assertEqual(len(doc.doc_id), 12)

    def test_missing_file(self):
        with self.assertRaises(DocumentError):
            load_document(DOCS / "nope.txt")

    def test_wrong_extension(self):
        with self.assertRaises(DocumentError):
            load_document(Path("notes.pdf"))

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "empty.txt"
            p.write_text("   \n", encoding="utf-8")
            with self.assertRaises(DocumentError):
                load_document(p)

    def test_missing_dir(self):
        with self.assertRaises(DocumentError):
            load_documents(Path("does-not-exist"))

    def test_iter_is_generator(self):
        gen = iter_documents(DOCS)
        self.assertTrue(hasattr(gen, "__next__"))
        docs = list(gen)
        self.assertGreaterEqual(len(docs), 7)

    def test_unique_ids(self):
        docs = load_documents(DOCS)
        ids = [d.doc_id for d in docs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_as_tuple(self):
        doc = load_document(DOCS / "os.txt")
        t = doc.as_tuple()
        self.assertIsInstance(t, tuple)
        self.assertEqual(len(t), 3)


if __name__ == "__main__":
    unittest.main()
