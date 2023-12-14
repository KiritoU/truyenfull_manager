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

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
