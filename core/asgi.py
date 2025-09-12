import os
from channels.routing import ProtocolTypeRouter, URLRouter
from .middleware import JWTAuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Import WebSocket URL patterns
from apps.notifications.urls import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})