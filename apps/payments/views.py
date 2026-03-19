from django.shortcuts import render
from rest_framework import generics
from .models import Payment
from .serializers import PaymentSerializer
from apps.users.permissions import IsUser
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema

# Create your views here.

@extend_schema(tags=["payments"])
class CreatePayemntView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsUser]
    
@extend_schema(tags=["payments"])
class PaymentDetaildView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsUser]
    filter_backends =[DjangoFilterBackend]
    filterset_fields = ['status']
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        if self.request.user.role == "STAFF":
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)
       
    