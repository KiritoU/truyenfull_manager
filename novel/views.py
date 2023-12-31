from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import render
from django.views.generic.list import ListView
from rest_framework import views, status, response, permissions
from urllib.parse import urlparse

from slugify import slugify

from .models import CrawlSource, Novel, Genre, Chapter
from .serializers import CrawlSourceSerializer, GenreSerializer, NovelDetailSerializer
from .tasks import update_novel_stats


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

    genres = Genre.objects.filter(novels__from_source=source).distinct()

    return render(
        request,
        "novel/source_detail.html",
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

    return render(
        request,
        "novel/genre_detail.html",
        {
            "novels": NovelDetailSerializer(novels, many=True).data,
            "source": source_name,
            "genre": genre_name,
            "genre_slug": genre_slug,
        },
    )


def novel_details(request, source_name, genre_slug, novel_slug):
    try:
        novel = Novel.objects.get(slug=novel_slug)
    except Novel.DoesNotExist:
        raise Http404("Novel does not exist")

    chapters = novel.chapters.all()

    return render(
        request,
        "novel/novel_detail.html",
        {
            "chapters": chapters,
            "novel": novel,
            "source": source_name,
            "genre_slug": genre_slug,
        },
    )


class ChapterListView(ListView):
    model = Chapter
    paginate_by = 100  # if pagination is desired
    template_name = "novel/novel_detail.html"

    def get_queryset(self) -> QuerySet[Any]:
        novel_slug = self.kwargs.get("novel_slug")

        queryset = Chapter.objects.filter(novel__slug=novel_slug)

        return queryset


class CrawlSourcesAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        sources = CrawlSource.objects.all()

        return response.Response(
            CrawlSourceSerializer(sources, many=True).data, status=status.HTTP_200_OK
        )


class GenreAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        source_name = request.query_params.get("source", "")
        genres = Genre.objects.all()
        if source_name:
            genres = genres.filter(novels__from_source__name=source_name).distinct()

        return response.Response(
            GenreSerializer(genres, many=True).data, status=status.HTTP_200_OK
        )


class NovelAndChapterUpdateAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        story_details = request.data.get("story_details", {})
        if story_details:
            href = story_details.get("href", "").strip("/")
            title = story_details.get("title", "")
            slug = story_details.get("slug", "")
            post_id = story_details.get("post_id", "")

            update_story_stats = request.data.get("update_story_stats", False)

            if update_story_stats:
                update_novel_stats.delay(title, slug, post_id, href)
                return response.Response({"message": "ok"})

            source_name = urlparse(href).netloc
            from_source, _ = CrawlSource.objects.get_or_create(name=source_name)

            novel, _ = Novel.objects.get_or_create(
                title=title,
                slug=slug,
                post_id=post_id,
                href=href,
                from_source=from_source,
            )

            genres = story_details.get("the-loai", "")
            for genre_name in genres.split(","):
                genre_name = genre_name.strip()

                genre, _ = Genre.objects.get_or_create(
                    name=genre_name, slug=slugify(genre_name)
                )

                novel.genres.add(genre)
                novel.save()

            chapters = story_details.get("chapters", {})
            for chapter_name, chapter_href in chapters.items():
                chapter_slug = get_chapter_slug(
                    chapter_name=chapter_name, story_title=title
                )
                chapter, _ = Chapter.objects.get_or_create(
                    name=chapter_name,
                    slug=chapter_slug,
                    href=chapter_href.strip("/"),
                    novel=novel,
                )

        crawled_chapters = request.data.get("crawled_chapters", [])
        for crawled_chapter in crawled_chapters:
            try:
                post_id = crawled_chapter.get("post_id", 0)
                if post_id:
                    story_title = crawled_chapter.get("story_title", "")
                    chapter_name = crawled_chapter.get("chapter_name", "")
                    chapter_href = crawled_chapter.get("chapter_href", "").strip("/")
                    chapter_post_id = crawled_chapter.get("chapter_post_id", 0)
                    novel = Novel.objects.get(post_id=post_id)

                    chapter_slug = get_chapter_slug(
                        chapter_name=chapter_name, story_title=story_title
                    )
                    chapter = Chapter.objects.get(
                        slug=chapter_slug,
                        name=chapter_name,
                        href=chapter_href,
                        novel=novel,
                    )

                    chapter.post_id = chapter_post_id
                    chapter.is_crawled = True
                    chapter.save()
            except:
                pass

        return response.Response({"message": "ok"})
