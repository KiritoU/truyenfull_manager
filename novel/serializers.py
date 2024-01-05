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
        res = {
            "all": novel.chapter_count,
            "crawled": novel.crawled_chapter_count,
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
        crawled_novels = novels.filter(is_crawled=True)

        return {
            "all": novels.count(),
            "crawled": crawled_novels.count(),
        }

    def get_chapters(self, source: CrawlSource) -> dict:
        chapters = Chapter.objects.filter(novel__from_source=source)
        crawled_chapters = chapters.filter(is_crawled=True)
        return {
            "all": chapters.count(),
            "crawled": crawled_chapters.count(),
        }
