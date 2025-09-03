from rest_framework import serializers
from django.db import transaction
from .models import (Cart, CartItem,Order,OrderItem)

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id","cart","menu_item","item_name","quantity","item_price","total_price"]
        read_only_fields = ["id","cart","item_price","total_price"]
        
    def validate_quantity(self, value):
        if value<=0:
            raise serializers.ValidationError("Quantity must be grater than 0")
        if value>100:
            raise serializers.ValidationError("Quantity must be less than 100")
        return value
    
    def validate_menu_item(self, value):
        if not value.is_available:
            raise serializers.ValidationError(f"Item {value.name} is no longer avilable for today")
        return value
    
    def validate(self, attrs):
        if self.instance is None:
            cart = attrs.get('cart') or Cart.objects.get_or_create(user =self.context['request'].user)[0]
            if CartItem.objects.filter(cart=cart, menu_item=attrs['menu_item']).exists():
                raise serializers.ValidationError("Item already exists in the cart.")
        return attrs
        

        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id","user","created_at","updated_at","cart_items"]
        read_only_fields = ["id","user","created_at","updated_at","cart_items"]
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id","user","status","total_amount","created_at","updated_at"]
        read_only_fields = ["order_id","user","total_amount","created_at","updated_at"]
        
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id","menu_item","item_name","price","quantity"]
        read_only_fields = ["id","menu_item","item_name","price","quantity"]
        
class OrderWithItemSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True,many=True)
    class Meta:
        model= Order
        fields = ["order_id","user","status","total_amount","items"]
        read_only_fields = ["order_id","user","status","total_amount","items"]

        
class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_id", "status", "total_amount", "created_at"]
        read_only_fields = ["order_id", "status", "total_amount", "created_at"]
        
    def create(self,validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            try:
                cart = Cart.objects.select_for_update().get(user=user)
            except Cart.DoesNotExist:
                    raise serializers.ValidationError("Cart is empty")
            
            cart_items = list(cart.cart_items.select_related("menu_item").select_for_update())
            if not cart_items:
                raise serializers.ValidationError("Cart has no items")
            
            
            total = 0
            for item in cart_items:
                current_price = item.menu_item.price
                if item.item_price != current_price:
                    raise serializers.ValidationError(f"Price changed for {item.menu_item.name}. please refresh your cart.")
                
                if not item.menu_item.is_available:
                    raise serializers.ValidationError(f"{item.menu_item.name} is no longer available for today ")
                
                total+=current_price* item.quantity
            if abs(total - sum(item.total_price for item in cart_items)) >0.01:
                raise serializers.ValidationError("Cart total is mismatch dectected")
                
                
            order = Order.objects.filter(user=user , status=Order.OrderStatus.PENDING).first()
            if order:
                order.items.all().delete()
            else:
                order = Order.objects.create(user=user, status=Order.OrderStatus.PENDING)
            total = 0
            for item in cart_items:
                if not item.menu_item.is_available:
                    raise serializers.ValidationError(f"Item {item.menu_item.name} is no longer avilable for today")
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