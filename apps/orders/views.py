from django.shortcuts import render
from rest_framework import viewsets,mixins,generics

# Create your views here.
from .models import (Cart, CartItem,Order,OrderItem)
from .serializers import (CartSerializer,CartItemSerializer,OrderSerializer,
                          OrderItemSerializer, CreateOrderSerializer)

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
        return CartItem.objects.select_related('menu_item','cart').filter(cart__user=self.request.user)
    
    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    # queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    