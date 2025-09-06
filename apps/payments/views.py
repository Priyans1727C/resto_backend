from django.shortcuts import render
from rest_framework import generics
from .models import Payment
from .serializers import PaymentSerializer
from apps.users.permissions import IsUser

# Create your views here.

class CreatePayemntView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsUser]
    
class PaymentDetaildView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsUser]
    def get_queryset(self):
        if self.request.user.role == "STAFF":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
       
    