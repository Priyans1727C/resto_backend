from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'status', 'method', 'amount', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('payment_id', 'order__id')
    ordering = ('-created_at',)
    readonly_fields = ('payment_id', 'created_at', 'updated_at')