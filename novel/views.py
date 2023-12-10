from django.http import Http404
from django.shortcuts import render
from rest_framework import views, status, response, permissions
from urllib.parse import urlparse

from slugify import slugify

from .models import CrawlSource, Novel, Genre, Chapter
from .serializers import CrawlSourceSerializer, GenreSerializer


def get_chapter_slug(chapter_name: str, story_title: str) -> str:
    return slugify(f"{story_title}-{chapter_name}")


def index(request):
    sources = CrawlSource.objects.all()
    return render(
        request,
        "novel/index.html",
        {"sources": CrawlSourceSerializer(sources, many=True).data},
    )


def source_details(request, source_name):
    try:
        source = CrawlSource.objects.get(name=source_name)
    except CrawlSource.DoesNotExist:
        raise Http404("Source does not exist")

    return render(
        request,
        "novel/source_detail_2.html",
        {"source": CrawlSourceSerializer(source).data},
    )


class CrawlSourcesAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        sources = CrawlSource.objects.all()

        return response.Response(
            CrawlSourceSerializer(sources, many=True).data, status=status.HTTP_200_OK
        )


class GenreAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        genres = Genre.objects.all()

        return response.Response(
            GenreSerializer(genres, many=True).data, status=status.HTTP_200_OK
        )
