from django.urls import path
from boards.consumers import BoardConsumer

websocket_urlpatterns = [
    path("ws/boards/<int:board_id>/", BoardConsumer.as_asgi()),
]
