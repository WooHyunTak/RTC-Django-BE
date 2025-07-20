from django.urls import path
from user.consumers import UserSocketConsumer

websocket_urlpatterns = [
    path("ws/users/", UserSocketConsumer.as_asgi()),
]
