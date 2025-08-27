from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

# Level 1: Restaurant
router = DefaultRouter()
router.register(r'restaurant', views.RestaurantViewSet, basename='restaurant')
router.register(r'getAllDetail',views.RestaurantItemsViewSet,basename="getallDetil")
router.register(r'menu-items',views.MenuItemViewSet,basename="category-menu-items")

# Level 2: Categories under restaurant
category_routes = NestedSimpleRouter(router, r'restaurant', lookup='restaurant')
category_routes.register(r'categories', views.CategoryViewSet, basename='restaurant-categories')

#Level 3: MenuItem under Categories
menuItem_routes = NestedSimpleRouter(category_routes,r'categories',lookup='categories')
menuItem_routes.register(r'menu-items',views.MenuItemViewSet,basename="category-menu-items")


# getAll = NestedSimpleRouter(router, r'', lookup='restaurant')
# router.register(r'getAll',views.RestaurantItemsViewSet,basename="getallDetil")

urlpatterns = [
    
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),
]

urlpatterns += router.urls
urlpatterns += category_routes.urls
urlpatterns += menuItem_routes.urls