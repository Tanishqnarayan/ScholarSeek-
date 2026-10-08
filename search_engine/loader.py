"""Document loading, validation and metadata (stdlib only)."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class DocumentError(Exception):
    """Raised for invalid or unreadable documents."""


@dataclass(frozen=True)
class Document:
    """Immutable document record with a stable unique id."""

    doc_id: str
    title: str
    filename: str
    category: str
    content: str
    word_count: int
    char_count: int
    content_hash: str
    loaded_at: str = field(compare=False)

    def as_tuple(self):
        """Return (doc_id, title, filename) immutable triple."""
        return (self.doc_id, self.title, self.filename)


def _doc_id_for(path: Path) -> str:
    """Stable id derived from relative filename (sha1, 12 hex chars)."""
    return hashlib.sha1(path.name.encode("utf-8")).hexdigest()[:12]


def _category_for(path: Path) -> str:
    """Category derived from filename stem, e.g. 'software_engineering' -> 'Software Engineering'."""
    return path.stem.replace("_", " ").title()


def load_document(path: Path) -> Document:
    """Load and validate a single .txt document.

    Raises:
        DocumentError: on wrong extension, missing file, empty file, decode errors.
    """
    path = Path(path)
    if path.suffix.lower() != ".txt":
        raise DocumentError(f"Unsupported extension for '{path}': only .txt allowed")
    if not path.exists() or not path.is_file():
        raise DocumentError(f"Missing file: {path}")
    try:
        content = path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise DocumentError(f"Cannot read '{path}': {exc}") from exc
    except OSError as exc:
        raise DocumentError(f"Cannot read '{path}': {exc}") from exc

    if not content.strip():
        raise DocumentError(f"Empty document: {path}")

    words = content.split()
    content_hash = hashlib.sha1(content.encode("utf-8")).hexdigest()
    return Document(
        doc_id=_doc_id_for(path),
        title=path.stem.replace("_", " ").title(),
        filename=path.name,
        category=_category_for(path),
        content=content,
        word_count=len(words),
        char_count=len(content),
        content_hash=content_hash,
        loaded_at=datetime.now(timezone.utc).isoformat(),
    )


def iter_documents(directory: Path):
    """Generator yielding Documents from a directory (skips invalid files)."""
    directory = Path(directory)
    if not directory.exists():
        raise DocumentError(f"Documents directory not found: {directory}")
    for path in sorted(directory.glob("*.txt")):
        try:
            yield load_document(path)
        except DocumentError:
            continue


def load_documents(directory: Path) -> list:
    """Load all valid .txt documents from a directory as a list."""
    return list(iter_documents(directory))
