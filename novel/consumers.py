# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from urllib.parse import urlparse

from slugify import slugify

from .models import CrawlSource, Novel, Genre, Chapter


def get_chapter_slug(chapter_name: str, story_title: str) -> str:
    return slugify(f"{story_title}-{chapter_name}")


class SourceConsumer(WebsocketConsumer):
    def connect(self):
        self.source_name = self.scope["url_route"]["kwargs"]["source_name"]
        self.room_group_name = f"source_{self.source_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        story_details = message.pop("story_details", {})
        if story_details:
            href = story_details.get("href", "").strip("/")
            title = story_details.get("title", "")
            slug = story_details.get("slug", "")
            post_id = story_details.get("post_id", "")

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

        crawled_chapter = message.pop("crawled_chapter", {})
        if crawled_chapter:
            try:
                post_id = crawled_chapter.get("post_id", 0)
                if post_id:
                    story_title = crawled_chapter.get("story_title", "")
                    chapter_name = crawled_chapter.get("chapter_name", "")
                    chapter_href = crawled_chapter.get("chapter_href", "").strip("/")
                    chapter_post_id = crawled_chapter.get("chapter_post_id", "")
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

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
