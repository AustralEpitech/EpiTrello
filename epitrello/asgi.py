"""
ASGI config for epitrello project with Django Channels.

Exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epitrello.settings")
django.setup()

import epitrello.routing  # noqa: E402

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(epitrello.routing.websocket_urlpatterns)
    ),
})
