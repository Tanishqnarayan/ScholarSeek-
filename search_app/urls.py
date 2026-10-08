from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("documents/<str:filename>/", views.document_detail, name="document_detail"),
    path("history/", views.history, name="history"),
    path("manage/", views.manage, name="manage"),
]
