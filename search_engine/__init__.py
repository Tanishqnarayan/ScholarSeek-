"""Mini Search Engine core package (stdlib only)."""

from .engine import SearchEngine
from .loader import Document, load_documents
from .preprocessor import preprocess, tokenize
from .indexer import InvertedIndex

__all__ = ["SearchEngine", "Document", "load_documents", "preprocess", "tokenize", "InvertedIndex"]
__version__ = "1.0.0"
