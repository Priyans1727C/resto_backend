from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    fields = ('menu_item', 'quantity', 'item_name', 'item_price', 'total_price')
    readonly_fields = ('item_name', 'item_price', 'total_price')
    raw_id_fields = ('menu_item',)
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('menu_item', 'quantity', 'price', 'item_name')
    readonly_fields = ('menu_item', 'quantity', 'price', 'item_name')
    extra = 0
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('order_id', 'username', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'user__username', 'user__email')
    readonly_fields = ('order_id', 'username', 'total_amount', 'created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'username', 'status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )