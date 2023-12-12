from django.http import Http404
from django.shortcuts import render
from rest_framework import views, status, response, permissions
from urllib.parse import urlparse

from slugify import slugify

from .models import CrawlSource, Novel, Genre, Chapter
from .serializers import CrawlSourceSerializer, GenreSerializer, NovelDetailSerializer


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

    genres = Genre.objects.filter(novels__from_source__name=source.name).distinct()

    return render(
        request,
        "novel/source_detail_2.html",
        {
            "source": {
                **CrawlSourceSerializer(source).data,
                "genres": GenreSerializer(genres, many=True).data,
            }
        },
    )


def genre_details(request, source_name, genre_slug):
    try:
        genre = Genre.objects.get(slug=genre_slug)
        genre_name = genre.name
    except:
        genre_name = genre_slug

    novels = Novel.objects.filter(
        from_source__name=source_name, genres__slug=genre_slug
    )

    print(NovelDetailSerializer(novels, many=True).data)

    return render(
        request,
        "novel/genre_detail.html",
        {
            "novels": NovelDetailSerializer(novels, many=True).data,
            "source": source_name,
            "genre": genre_name,
        },
    )


class CrawlSourcesAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        sources = CrawlSource.objects.all()

        return response.Response(
            CrawlSourceSerializer(sources, many=True).data, status=status.HTTP_200_OK
        )


class GenreAPIView(views.APIView):
    def get(self, request, *args, **kwargs):
        source_name = request.query_params.get("source", "")
        genres = Genre.objects.all()
        if source_name:
            genres = genres.filter(novels__from_source__name=source_name).distinct()

        return response.Response(
            GenreSerializer(genres, many=True).data, status=status.HTTP_200_OK
        )
