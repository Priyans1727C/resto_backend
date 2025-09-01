from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_nested.routers import NestedSimpleRouter

router = DefaultRouter()
router.register("cart",views.CartViewSet, basename="cart")

cart_item = NestedSimpleRouter(router,r"cart",lookup="cart")
cart_item.register(r"items",views.CartItemViewSet,basename="cart_items")

router.register("cartItem",views.CartItemViewSet, basename="cart_item")
router.register("getAllOrder",views.OrderViewSet,basename="orders")
router.register("getAllOrderItem",views.OrderItemViewSet,basename="order-items")

urlpatterns = [
    path("create/",views.CreateOrderView.as_view(),name="create-order"),
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),

]+router.urls+cart_item.urls
