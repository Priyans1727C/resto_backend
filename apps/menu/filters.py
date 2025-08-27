import django_filters
from .models import MenuItem

class ItemFilters(django_filters.FilterSet):
    class Meta:
        model = MenuItem
        fields = {
            "name":["exact","contains"],
            "description":["exact","contains"],
            "price":["gt","lt","range"]
        }