from django.contrib import admin

from .models import Document, SearchQuery, SearchResult


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "filename", "category", "word_count", "updated_at")
    search_fields = ("title", "filename", "category")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("query_text", "result_count", "searched_at")
    search_fields = ("query_text",)


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ("doc_filename", "relevance_score", "query", "searched_at")
    list_filter = ("searched_at",)
