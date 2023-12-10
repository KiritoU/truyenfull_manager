from django.contrib import admin

from .models import CrawlSource, Novel, Genre, Chapter

admin.site.register(CrawlSource)
admin.site.register(Novel)
admin.site.register(Genre)
admin.site.register(Chapter)
