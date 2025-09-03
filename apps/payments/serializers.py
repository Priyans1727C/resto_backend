from rest_framework import serializers
from .models import Payment, Order
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.UUIDField(write_only=True)
    class Meta:
        model = Payment
        fields = ["payment_id", "order", "method", "status", "amount", "created_at"]
        read_only_fields = ["payment_id", "status", "amount", "created_at"]

    def validate_order(self, value):
        if not self.instance:
            if Payment.objects.filter(order__order_id=value).exists():
                raise serializers.ValidationError(f"payment already exist for order {value}")
        return value


    def validate(self, attrs):
        order_id = attrs['order']
        print(attrs)
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order": "Order does not exist."})

        if order.total_amount <=0:
            raise serializers.ValidationError("Order amount must be grater then 0")
        
        if order.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.CONFIRMED]:
            raise serializers.ValidationError("Order can not be paid")
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                order = validated_data.pop("order")
                order = Order.objects.select_for_update().get(pk=order)
                
                request = self.context.get('request')
                if order.user != request.user:
                    raise PermissionDenied("you don't own this order")
                
                if order.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.CONFIRMED]:
                    raise PermissionDenied("Order can't be paid")
                
                payment = Payment.objects.create(order=order, amount=order.total_amount, **validated_data)

                if payment.method == Payment.PaymentMethod.COD:
                    payment.status = Payment.PaymentStatus.SUCCESS
                    order.status = Order.OrderStatus.CONFIRMED
                elif payment.method == Payment.PaymentMethod.ONLINE:
                    payment.status = Payment.PaymentStatus.PENDING
                    
                payment.save()
                order.save()

                return payment
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})