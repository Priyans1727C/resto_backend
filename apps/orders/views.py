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
        return Cart.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsUser]
    

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
