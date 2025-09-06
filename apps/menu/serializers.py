from rest_framework import serializers
from .models import Restaurant,Category,MenuItem
from rest_framework.validators import UniqueValidator
from django.db import transaction

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
    image = serializers.ImageField(required=False, allow_null=True,use_url =True)
    remove_image = serializers.BooleanField(write_only=True,required=False,default=False)
    class Meta:
        model = MenuItem
        fields = ["category","name","slug","description","is_available","serving_size","price","image","remove_image"]
        read_only_fields = ["slug"]
    
    def validate_image(self,image):
        if image:
            MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024 
            if image.size > MAX_PROFILE_IMAGE_SIZE:
                raise serializers.ValidationError(f"Image size should be <= {MAX_PROFILE_IMAGE_SIZE // (1024*1024)} MB.")
        return image
    
    @transaction.atomic
    def update(self,instance, validated_data):
        if validated_data.pop('remove_image',False):
            if instance.image:
                try:
                    instance.image.delete(save=False)
                except Exception:
                    pass
                
            instance.image = None
        
        image = validated_data.get('image',serializers.empty)
        if image is not serializers.empty:
            instance.image = image
        for attr,value in validated_data.items():
            if attr !='image':
                setattr(instance,attr,value)
                
        instance.save()
        return instance
    
            
       
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