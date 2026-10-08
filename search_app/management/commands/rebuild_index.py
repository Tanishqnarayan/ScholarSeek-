"""Rebuild the JSON inverted index and sync the Document catalog."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Rebuild data/index.json from documents/ and sync Document rows."

    def handle(self, *args, **options):
        from search_app.services import refresh_engine
        from search_app.models import Document
        from search_engine.loader import load_document

        docs_dir = Path(settings.DOCUMENTS_DIR)
        if not docs_dir.exists():
            raise CommandError(f"Documents dir missing: {docs_dir}")
        engine = refresh_engine()
        stats = engine.build_index(docs_dir)
        engine.save_index(Path(settings.INDEX_PATH))
        count = 0
        for doc_id, meta in engine.index.documents.items():
            Document.objects.update_or_create(
                filename=meta.filename,
                defaults={
                    "title": meta.title,
                    "category": meta.category,
                    "content_hash": meta.content_hash,
                    "word_count": meta.word_count,
                },
            )
            count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Indexed {stats['documents']} documents, "
                f"{stats['unique_terms']} terms. Catalog rows: {count}."
            )
        )
