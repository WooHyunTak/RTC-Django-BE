"""
ASGI config for rtc_django_chat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from common.middlewares.websocket_jwt import WebsocketJWTAuthentication
from rtc_django_chat.routings import websocket_urlpatterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rtc_django_chat.settings")

application = get_asgi_application()
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": WebsocketJWTAuthentication(URLRouter(websocket_urlpatterns)),
    }
)
