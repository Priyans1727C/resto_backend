from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import (Restaurant,Category,MenuItem)
from .serializers import (OnlyRestaurantSerializer,OnlyCategoriesSerializer,OnlyMenuItemSerializer,RestaurantItemsSeializer)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import ItemFilters

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.users.permissions import IsStaffOrReadOnly


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = OnlyRestaurantSerializer
    lookup_field ="slug"
    permission_classes = [IsStaffOrReadOnly]
    throttle_scope = "resto_details"
    

# class CategoryViewSet(viewsets.ModelViewSet):
#     queryset = Category.objects.prefetch_related("items")
#     serializer_class = OnlyCategoriesSerializer
#     lookup_field = "slug"

# class MenuItemViewSet(viewsets.ModelViewSet):
#     queryset = MenuItem.objects.select_related("category")
#     serializer_class = OnlyMenuItemSerializer
#     lookup_field = "slug"
    

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = OnlyCategoriesSerializer
    lookup_field = "slug"
    permission_classes = [IsStaffOrReadOnly]
    throttle_scope = "resto_details"
    
    def get_queryset(self):
        resto_slug = self.kwargs.get("restaurant_slug")
        return Category.objects.filter(restaurant__slug = resto_slug).prefetch_related("items")
       

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = OnlyMenuItemSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_class = ItemFilters
    # filterset_fields = ['category','price',]
    search_fields = ['name', 'description']
    permission_classes = [IsStaffOrReadOnly]
    throttle_scope = "resto_details"
    
    def get_queryset(self):
        category_slug = self.kwargs.get("categories_slug",None)
        resto_slug = self.kwargs.get("restaurant_slug",None)
        if category_slug is None and resto_slug is None:
            return MenuItem.objects.all()
        return MenuItem.objects.filter(
            category__slug=category_slug,
            category__restaurant__slug=resto_slug
        ).select_related("category__restaurant")
        
    @method_decorator(cache_page(60*60*2,key_prefix="menu_items"))
    def list(self,*args,**kwargs):
        return super().list(self,args,kwargs)
        
        
    
class RestaurantItemsViewSet(viewsets.ReadOnlyModelViewSet):
    """It is for getting all the details of perticurar resto (inclide resto-name,category,items)"""
    queryset = Restaurant.objects.all().prefetch_related("categories__items")
    serializer_class = RestaurantItemsSeializer
    lookup_field ="slug"
    permission_classes = [IsStaffOrReadOnly]
    throttle_scope = "resto_details"
    def get_queryset(self):
        return super().get_queryset()
    
    @method_decorator(cache_page(60*60*20,key_prefix="resto_details"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)




