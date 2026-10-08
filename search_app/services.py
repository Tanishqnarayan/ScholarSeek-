"""Shared SearchEngine singleton (loads persisted JSON index, rebuilds if missing)."""

import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

_engine = None


def get_engine():
    """Return a cached SearchEngine backed by settings.DOCUMENTS_DIR/INDEX_PATH."""
    global _engine
    if _engine is not None:
        return _engine
    from search_engine.engine import SearchEngine

    documents_dir = Path(settings.DOCUMENTS_DIR)
    index_path = Path(settings.INDEX_PATH)
    engine = SearchEngine(documents_dir=documents_dir, index_path=index_path)
    try:
        if index_path.exists():
            engine.load_index(index_path)
        else:
            engine.build_index(documents_dir)
            engine.save_index(index_path)
    except Exception as exc:  # missing/empty docs dir must not crash Django boot
        logger.warning("Search index unavailable: %s", exc)
    _engine = engine
    return _engine


def refresh_engine():
    """Force rebuild (used after uploads / management command)."""
    global _engine
    _engine = None
    return get_engine()
