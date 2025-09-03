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
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    