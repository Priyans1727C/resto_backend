from django.db import models
import uuid
from apps.orders.models import Order
# Create your models here.

class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        COD = "COD","Cash On Delivery"
        ONLINE = "ONLINE" ,"Online Payment"
        
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED" , "Failed"
    
    payment_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order = models.OneToOneField(Order,on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_id}"
    
