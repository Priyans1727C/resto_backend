from rest_framework import serializers
from django.db import transaction
from .models import (Cart, CartItem,Order,OrderItem)

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id","cart","menu_item","item_name","quantity","item_price","total_price"]
        read_only_fields = ["id","cart"]
        
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id","user","created_at","updated_at","cart_items"]
        read_only_fields = ["id","cart_items"]
        
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
        
class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id", "status", "total_amount", "created_at"]
        read_only_fields = ["order_id", "status", "total_amount", "created_at"]
        
    def create(self,validated_data):
        user = self.context["request"].user
        try:
            cart = user.cart
        except Cart.DoesNotExist:
                raise serializers.ValidationError("Cart is empty")
        
        if not cart.cart_items.exists():
            raise serializers.ValidationError("Cart has no items")
        
        with transaction.atomic():
            order = Order.objects.create(user=user, status=Order.OrderStatus.PENDING)
            total = 0
            for item in cart.cart_items.select_related("menu_item"):
                price = item.menu_item.price * item.quantity
                total += price

                OrderItem.objects.create(
                    order=order,
                    menu_item=item.menu_item,
                    price=item.menu_item.price,  # snapshot price
                    quantity=item.quantity
                )

            order.total_amount = total
            order.save()

            cart.cart_items.all().delete()
            cart.delete()

        return order