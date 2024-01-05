from django.conf import settings
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "novelnchapterupdate/",
        views.NovelAndChapterUpdateAPIView.as_view(),
        name="novelnchapterupdate",
    ),
    path("sources-info/", views.CrawlSourcesAPIView.as_view(), name="crawl_sources"),
    path("genres-info/", views.GenreAPIView.as_view(), name="genre_infos"),
    path(
        "<str:source_name>/<str:genre_slug>/<str:novel_slug>/",
        views.novel_details,
        # views.ChapterListView.as_view(),
        name="novel_details",
    ),
    path(
        "<str:source_name>/<str:genre_slug>/",
        views.genre_details,
        name="genre_details",
    ),
    path("<str:source_name>/", views.source_details, name="source_details"),
]
