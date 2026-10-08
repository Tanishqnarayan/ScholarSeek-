"""Tests for preprocessing: lowercase, punctuation, tokenize, stopwords."""

import unittest

from search_engine.preprocessor import (
    STOP_WORDS,
    normalize,
    preprocess,
    remove_stopwords,
    tokenize,
)


class TestPreprocessor(unittest.TestCase):
    def test_spec_example(self):
        self.assertEqual(
            preprocess("Python is a high-level programming language."),
            ["python", "high", "level", "programming", "language"],
        )

    def test_lowercase_and_punctuation(self):
        self.assertEqual(preprocess("Hello, WORLD!"), ["hello", "world"])

    def test_whitespace_normalization(self):
        self.assertEqual(normalize("  a   b\nc\t"), "a b c")

    def test_stopword_removal(self):
        self.assertEqual(remove_stopwords(["the", "python", "and", "code"]), ["python", "code"])

    def test_invalid_tokens_removed(self):
        self.assertEqual(preprocess("a I x"), [])

    def test_stopwords_is_set(self):
        self.assertIsInstance(STOP_WORDS, frozenset)
        self.assertIn("the", STOP_WORDS)

    def test_none_raises(self):
        with self.assertRaises(ValueError):
            preprocess(None)

    def test_tokenize_returns_list(self):
        tokens = tokenize("Data Structures and Algorithms")
        self.assertIsInstance(tokens, list)
        self.assertIn("data", tokens)


if __name__ == "__main__":
    unittest.main()
