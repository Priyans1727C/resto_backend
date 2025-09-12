from django.urls import path
from . import consumers
urlpatterns = [
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),
]

websocket_urlpatterns = [
    path('ws/sc/',consumers.MySyncConsumer.as_asgi()),
   
]