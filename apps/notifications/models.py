from django.db import models
import uuid
from django.conf import settings


User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        ORDER = "ORDER", "Order"
        PAYMENT = "PAYMENT", "Payment"
        GENERAL = "GENERAL", "General"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=15,choices=NotificationType.choices, default=NotificationType.GENERAL)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=800)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self):
        return self.title
    
