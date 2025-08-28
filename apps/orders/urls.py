from django.urls import path
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),

]
