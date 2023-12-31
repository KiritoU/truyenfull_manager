from django.db.models import BooleanField, Case, When, Value
from django.db.models import F, Q, Value, CharField
from rest_framework import serializers

from .models import CrawlSource, Novel, Genre, Chapter


class GenreSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
            "slug",
            "stats",
        ]

    def get_stats(self, genre: Genre) -> dict:
        return genre.get_statistics()


class NovelDetailSerializer(serializers.ModelSerializer):
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = Novel
        fields = [
            "id",
            "title",
            "slug",
            "chapters",
        ]

    def get_chapters(self, novel: Novel) -> dict:
        chapters = novel.chapters.all()
        crawled_chapters = chapters.filter(is_crawled=True)
        res = {
            "all": chapters.count(),
            "crawled": crawled_chapters.count(),
        }

        res["status"] = (
            "Đủ"
            if res["all"] == res["crawled"]
            else f'Còn {res["all"] - res["crawled"]}'
        )

        return res


class CrawlSourceSerializer(serializers.ModelSerializer):
    novels = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()

    class Meta:
        model = CrawlSource
        fields = [
            "id",
            "name",
            "novels",
            "chapters",
        ]

    def get_novels(self, source: CrawlSource) -> dict:
        novels = source.novels.all()

        crawled_novels = 0
        for novel in novels:
            is_not_crawled_chapter_exist = novel.chapters.filter(
                is_crawled=False
            ).exists()
            if not is_not_crawled_chapter_exist:
                crawled_novels += 1

        return {
            "all": novels.count(),
            "crawled": crawled_novels,
        }

    def get_chapters(self, source: CrawlSource) -> dict:
        chapters = Chapter.objects.filter(novel__from_source=source)
        crawled_chapters = chapters.filter(is_crawled=True)
        return {
            "all": chapters.count(),
            "crawled": crawled_chapters.count(),
        }
