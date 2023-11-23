from django.urls import re_path, path

from . import consumer

websocket_urlpatterns = [
    re_path(r"ws/exchange/(?P<room_name>\w+)/$", consumer.SocketConsumer.as_asgi()),
]