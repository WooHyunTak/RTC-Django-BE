"""
ASGI config for rtc_django_chat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rtc_django_chat.settings")

# Django 초기화 이후에 WebSocket 관련 모듈을 import 해야 AppRegistryNotReady를 피할 수 있음
django_asgi_app = get_asgi_application()

from common.middlewares.websocket_jwt import WebsocketJWTAuthentication  # noqa: E402
from rtc_django_chat.routings import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebsocketJWTAuthentication(URLRouter(websocket_urlpatterns)),
    }
)
