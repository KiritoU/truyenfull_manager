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

    def __str__(self):
        return self.name

    def get_statistics(self):
        novels = self.novels.all()
        result = {
            "novels": {"all": novels.count(), "crawled": 0},
            "chapters": {"all": 0, "crawled": 0},
        }

        for novel in novels:
            chapters = novel.chapters.all()
            crawled_chapters = chapters.filter(is_crawled=True)

            chapters_count = chapters.count()
            crawled_chapters_count = crawled_chapters.count()

            result["chapters"]["all"] += chapters_count
            result["chapters"]["crawled"] += crawled_chapters_count

            if chapters_count == crawled_chapters_count:
                result["novels"]["crawled"] += 1

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
