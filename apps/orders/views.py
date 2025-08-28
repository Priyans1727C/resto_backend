from django.shortcuts import render
from rest_framework import viewsets,mixins
# Create your views here.
from .models import (Cart, CartItem,Order,OrderItem)
from .serializers import (CartSerializer,CartItemSerializer,OrderSerializer,OrderItemSerializer)

from apps.users.permissions import IsStaffOrReadOnly, IsUser


class SafeBaseViewSet(mixins.CreateModelMixin,mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass

class CartViewSet(SafeBaseViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsUser]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related('cart_items')
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsUser]
    
    def get_queryset(self):
        cart_id = self.kwargs.get("cart_pk",None)
        return CartItem.objects.filter(cart = cart_id).select_related("cart","menu_item")
    

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
