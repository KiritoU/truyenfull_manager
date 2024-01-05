from django.db import models


def get_empty_string():
    return ""


class CrawlSource(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)

    novel_count = models.IntegerField(null=True, blank=True, default=0)
    crawled_novel_count = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name

    def get_statistics(self):
        result = {
            "novels": {
                "all": self.novel_count,
                "crawled": self.crawled_novel_count,
            }
        }

        return result


class Novel(models.Model):
    title = models.CharField(
        max_length=255, null=True, blank=True, default=get_empty_string
    )
    slug = models.CharField(max_length=255)
    href = models.CharField(max_length=255)

    post_id = models.IntegerField(null=True, blank=True, default=0)

    from_source = models.ForeignKey(
        CrawlSource, related_name="novels", on_delete=models.CASCADE
    )

    chapter_count = models.IntegerField(null=True, blank=True, default=0)
    crawled_chapter_count = models.IntegerField(null=True, blank=True, default=0)

    is_crawled = models.BooleanField(null=True, blank=True, default=False)

    genres = models.ManyToManyField(Genre, blank=True, related_name="novels")

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_source}: {self.title}"

    # @property
    # def is_crawled(self):
    #     return True


class Chapter(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    href = models.CharField(max_length=255)

    post_id = models.IntegerField(null=True, blank=True, default=0)
    is_crawled = models.BooleanField(default=False)

    novel = models.ForeignKey(Novel, related_name="chapters", on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.novel.title} Chapter: {self.name}"
