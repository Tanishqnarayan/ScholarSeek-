"""Web views: home, search, document detail, history, upload."""

from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404, redirect, render

from search_engine.snippets import highlight_snippet

from .models import Document, SearchQuery, SearchResult
from .services import get_engine, refresh_engine

PER_PAGE = 5
POPULAR = ["Python", "Database normalization", "Algorithms", "Operating Systems"]


def home(request):
    """Landing page with search box + popular searches."""
    return render(request, "search_app/home.html", {"popular": POPULAR})


def search(request):
    """Run query through the core engine, persist history, paginate."""
    query_text = (request.GET.get("q", "") or "").strip()
    page_no = request.GET.get("page", 1)
    if not query_text:
        messages.info(request, "Type a query to search the document collection.")
        return redirect("home")

    engine = get_engine()
    try:
        hits = engine.search(query_text, top_k=50)
    except ValueError as exc:
        messages.error(request, f"Invalid query: {exc}")
        return redirect("home")

    # Persist query + hits (failures must not break search display).
    try:
        query_obj = SearchQuery.objects.create(query_text=query_text, result_count=len(hits))
        for hit in hits:  # loop over ranked hits
            doc = Document.objects.filter(filename=hit["filename"]).first()
            SearchResult.objects.create(
                query=query_obj,
                document=doc,
                doc_filename=hit["filename"],
                relevance_score=hit["relevance"],
                snippet=hit["snippet"][:1000],
            )
    except DatabaseError:
        query_obj = None

    # Highlight snippets for display.
    from search_engine.query_parser import parse_query

    parsed = parse_query(query_text)
    for hit in hits:
        hit["snippet_html"] = highlight_snippet(hit["snippet"], parsed.tokens)

    paginator = Paginator(hits, PER_PAGE)
    try:
        page = paginator.page(page_no)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)

    return render(
        request,
        "search_app/results.html",
        {"query": query_text, "page_obj": page, "total": len(hits)},
    )


def document_detail(request, filename):
    """Full document view with metadata."""
    engine = get_engine()
    doc = next(
        (d for d in engine.index.documents.values() if d.filename == filename),
        None,
    )
    if doc is None:
        # Fall back to DB catalog for a nicer 404 context.
        get_object_or_404(Document, filename=filename)
        return render(request, "search_app/document.html", {"doc": None, "filename": filename})
    return render(
        request,
        "search_app/document.html",
        {"doc": doc, "filename": filename, "content_lines": doc.content.splitlines()},
    )


def history(request):
    """Recent searches with their top hits."""
    queries = SearchQuery.objects.prefetch_related("results")[:30]
    return render(request, "search_app/history.html", {"queries": queries})


@staff_member_required
def manage(request):
    """Staff document management: list catalog + upload .txt + rebuild index."""
    docs_dir = Path(settings.DOCUMENTS_DIR)
    if request.method == "POST" and request.FILES.get("file"):
        upload = request.FILES["file"]
        if not upload.name.lower().endswith(".txt"):
            messages.error(request, "Only .txt files are allowed.")
        elif upload.size == 0:
            messages.error(request, "Empty file rejected.")
        elif upload.size > 2 * 1024 * 1024:
            messages.error(request, "File too large (max 2 MB).")
        else:
            dest = docs_dir / Path(upload.name).name
            docs_dir.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as fh:
                for chunk in upload.chunks():
                    fh.write(chunk)
            try:
                engine = refresh_engine()
                stats = engine.build_index(docs_dir)
                engine.save_index(Path(settings.INDEX_PATH))
                # Sync DB catalog.
                from search_engine.loader import load_document

                meta = load_document(dest)
                Document.objects.update_or_create(
                    filename=meta.filename,
                    defaults={
                        "title": meta.title,
                        "category": meta.category,
                        "content_hash": meta.content_hash,
                        "word_count": meta.word_count,
                    },
                )
                messages.success(request, f"Indexed {upload.name} ({stats['documents']} docs).")
            except Exception as exc:  # noqa: BLE001 - surface to staff UI
                messages.error(request, f"Indexing failed: {exc}")
        return redirect("manage")

    engine = get_engine()
    indexed = sorted(engine.index.documents.values(), key=lambda d: d.filename)
    return render(request, "search_app/manage.html", {"indexed": indexed})
