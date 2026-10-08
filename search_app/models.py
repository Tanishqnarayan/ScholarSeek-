"""Persistent app data (MySQL). The inverted index itself stays in data/index.json."""

from django.db import models


class Document(models.Model):
    """Catalog entry for a .txt file in documents/."""

    title = models.CharField(max_length=255)
    filename = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, db_index=True)
    content_hash = models.CharField(max_length=64, blank=True)
    word_count = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [models.Index(fields=["category"], name="doc_category_idx")]

    def __str__(self):
        return f"{self.title} ({self.filename})"


class SearchQuery(models.Model):
    """One user search (query text + when + how many hits)."""

    query_text = models.CharField(max_length=500, db_index=True)
    result_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-searched_at"]
        indexes = [models.Index(fields=["query_text"], name="query_text_idx")]

    def __str__(self):
        return self.query_text


class SearchResult(models.Model):
    """One (query, document) hit stored for history."""

    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name="results")
    document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, blank=True, related_name="hits"
    )
    doc_filename = models.CharField(max_length=255, default="")
    relevance_score = models.FloatField(default=0.0)
    snippet = models.TextField(blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-relevance_score"]
        indexes = [models.Index(fields=["query", "-relevance_score"], name="result_query_idx")]

    def __str__(self):
        return f"{self.doc_filename}: {self.relevance_score}%"
