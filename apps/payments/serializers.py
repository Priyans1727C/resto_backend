from rest_framework import serializers
from .models import Payment, Order
from django.db import transaction

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(write_only = True)
    class Meta:
        model = Payment
        fields = ["payment_id","order_id","method","status","amount","created_at"]
        read_only_fields = ["payment_id","status","amount","created_at"]
        
    def create(self, validated_data):
        order_id = validated_data.pop("order_id")
        try:
            with transaction.atomic():
                order = Order.objects.get(order_id=order_id)
                payment = Payment.objects.create(order=order, amount=order.total_amount, **validated_data)

                if payment.method == Payment.PaymentMethod.COD:
                    payment.status = Payment.PaymentStatus.SUCCESS
                    payment.save()
                    order.status = Order.OrderStatus.CONFIRMED
                    order.save()

                return payment
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "Order does not exist."})
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})