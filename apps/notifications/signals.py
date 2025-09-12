from django.db.models.signals import post_save
from apps.orders.models import Order
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

@receiver(post_save, sender=Order)
def sent_notify(sender, instance, created, **kwargs):
    print("singal trigreed")
    if not created:
        notification = Notification.objects.create(
            user=instance.user,
            type="ORDER",
            title="Order Update",
            message=f"Your order {instance.order_id} is now {instance.status}."
        )
        channel_layer = get_channel_layer()
        if channel_layer is None:
            print("channel_layer is None! Check configuration.")

        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                "type": "send_notification",
                "data": {
                    "id": str(notification.id),
                    "notification_type":notification.type,
                    "order_instance": {
                        "id":str(instance.order_id),
                        "status":instance.status,
                        },
                    
                    "title": notification.title,
                    "message": notification.message,
                    
                    "created_at": str(notification.created_at),
                    "is_read": notification.is_read,
                    
                },
            },
        )
    