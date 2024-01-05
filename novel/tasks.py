from urllib.parse import urlparse

from celery import shared_task

from .models import CrawlSource, Novel


@shared_task()
def update_novel_stats(title, slug, post_id, href) -> True:
    source_name = urlparse(href).netloc
    from_source, _ = CrawlSource.objects.get_or_create(name=source_name)

    try:
        novel = Novel.objects.get(
            title=title,
            slug=slug,
            post_id=post_id,
            href=href,
            from_source=from_source,
        )

        chapters = novel.chapters.all()
        crawled_chapters = chapters.filter(is_crawled=True)

        novel.chapter_count = chapters.count()
        novel.crawled_chapter_count = crawled_chapters.count()
        novel.is_crawled = novel.chapter_count == novel.crawled_chapter_count

        novel.save()

        genres = novel.genres.all()
        for genre in genres:
            genre_novels = genre.novels.all()
            genre_crawled_novels = genre_novels.filter(is_crawled=True)

            genre.novel_count = genre_novels.count()
            genre.crawled_novel_count = genre_crawled_novels.count()

            genre.save()

        return True
    except Exception as e:
        return e
