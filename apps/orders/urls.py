from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("cart",views.CartViewSet, basename="cart")
router.register("cartItem",views.CartItemViewSet)
router.register("getAllOrder",views.OrderViewSet)
router.register("getAllOrderItem",views.OrderItemViewSet)

urlpatterns = [
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),

]+router.urls
