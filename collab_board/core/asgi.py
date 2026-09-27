"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import canvas.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    # No AuthMiddlewareStack: this app has no logged-in users — each browser
    # tab gets a random name/color client-side — so a WebSocket connection
    # never needs to touch the database. Removing it also avoids depending
    # on the session table existing at all.
    "websocket": URLRouter(
        canvas.routing.websocket_urlpatterns
    ),
})