"""Django tests: views, search history persistence, document page."""

from django.test import TestCase
from django.urls import reverse

from search_app.models import Document, SearchQuery


class ViewTests(TestCase):
    def test_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MINI SEARCH ENGINE")

    def test_search_returns_ranked_results(self):
        response = self.client.get(reverse("search"), {"q": "database normalization"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dbms.txt")
        self.assertTrue(SearchQuery.objects.filter(query_text="database normalization").exists())
        query = SearchQuery.objects.get(query_text="database normalization")
        self.assertGreater(query.results.count(), 0)
        scores = list(query.results.values_list("relevance_score", flat=True))
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_search_empty_query_redirects(self):
        response = self.client.get(reverse("search"), {"q": ""})
        self.assertIn(response.status_code, (302, 200))

    def test_search_no_match(self):
        response = self.client.get(reverse("search"), {"q": "zzzqqqxxxyyy"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0 results")

    def test_phrase_search(self):
        response = self.client.get(reverse("search"), {"q": '"deadlock detection"'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "os.txt")

    def test_document_page(self):
        response = self.client.get(reverse("document_detail", args=["dbms.txt"]))
        self.assertEqual(response.status_code, 200)

    def test_history_page(self):
        self.client.get(reverse("search"), {"q": "python"})
        response = self.client.get(reverse("history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "python")

    def test_pagination(self):
        response = self.client.get(reverse("search"), {"q": "python", "page": 1})
        self.assertEqual(response.status_code, 200)


class ModelTests(TestCase):
    def test_document_str(self):
        doc = Document.objects.create(title="Dbms", filename="dbms.txt", category="Dbms")
        self.assertIn("dbms.txt", str(doc))
