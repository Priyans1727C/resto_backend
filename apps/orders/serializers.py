from rest_framework import serializers
from .models import (Cart, CartItem,Order,OrderItem)

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id","user","created_at","updated_at"]
        read_only_fields = ["id"]
        
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id","cart","menu_item","item_name","quantity","item_price","total_price"]
        read_only_fields = ["id"]
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id","user","status","total_amount","created_at","updated_at"]
        read_only_fields = ["order_id"]
        
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id","menu_item","item_name","price","quantity"]
        read_only_fields = ["id"]
        