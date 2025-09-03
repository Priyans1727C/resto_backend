from rest_framework import serializers
from .models import Restaurant,Category,MenuItem
from rest_framework.validators import UniqueValidator


class OnlyRestaurantSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=Restaurant.objects.all(),
                lookup='iexact',  # This performs a case-insensitive check
                message="A restaurant with this name already exists."
            )
        ]
    )
    class Meta:
        model = Restaurant
        fields = ["id","name","slug","address","description","email"]
        read_only_fields = ["id","slug"]
   
   
class OnlyMenuItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=MenuItem.objects.all(),
                lookup='iexact',  # This performs a case-insensitive check
                message="A restaurant with this name already exists."
            )
        ]
    )
    class Meta:
        model = MenuItem
        fields = ["category","name","slug","description","is_available","serving_size","price"]
        read_only_fields = ["slug"]     
       
class OnlyCategoriesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=Category.objects.all(),
                lookup='iexact',  # This performs a case-insensitive check
                message="A restaurant with this name already exists."
            )
        ]
    )
    class Meta:
        model = Category
        fields = ["restaurant","name","slug","items"]
        read_only_fields = ["slug","items"]
        
class CategoriesWithItemSerializer(serializers.ModelSerializer):
    items = OnlyMenuItemSerializer(many=True,read_only=True)
    class Meta:
        model = Category
        fields = ["id","name","slug","items"]


class RestaurantItemsSeializer(serializers.ModelSerializer):
    categories  = CategoriesWithItemSerializer(many=True,read_only=True)
    class Meta:
        model = Restaurant
        fields =  ["name","slug","address","description","email","categories"]