from django.contrib import admin
from .models import Payment
# Register your models here.

@admin.register(Payment)
class OrderAdmin(admin.ModelAdmin):
    pass
    