# yourapp/admin.py
from django.contrib import admin
from .models import Restaurant, Category, MenuItem

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'address')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active', 'city')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'is_active', 'created_at')
    search_fields = ('name', 'restaurant__name')
    list_filter = ('is_active', 'restaurant')
    prepopulated_fields = {'slug': ('name',)}

    # Optional: If you decide to use unique_together, add it back to your model
    # and use this method to display a clear error message.
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['name'].unique_together_error = "This category name already exists for this restaurant."
    #     return form


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_vegetarian')
    list_editable = ('price', 'is_available')
    list_filter = ('category', 'is_vegetarian', 'is_available')
    search_fields = ('name', 'description')
    readonly_fields = ('slug',) # Make the slug field read-only since it's auto-generated
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'description')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'is_available', 'is_vegetarian', 'serving_size')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )