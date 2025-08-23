from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from django.db import transaction
from rest_framework.response import Response

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "phone_number", "address", "date_of_birth"]

class UserSafeSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role", "is_email_verified", "date_joined", "last_login","profile")
        read_only_fields = ("id","role","is_email_verified","date_joined", "last_login")
    

    

class UpdateUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ("full_name","profile")
        # read_only_fields =("email")
        
    def validate_full_name(self, value):
        if not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError("Only Letter allowed")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        user_data = validated_data.get("full_name", None)
        if user_data:
            for attr, val in validated_data.items():
                setattr(instance, attr, val)
            instance.save(update_fields=list(validated_data.keys()) if validated_data else None)

        if profile_data:
            updated_count = UserProfile.objects.filter(user=instance).update(**profile_data)
            if updated_count:
                profile_obj = getattr(instance, "profile", None)
                if profile_obj:
                    for k, v in profile_data.items():
                        setattr(profile_obj, k, v)
            else:
                new_profile = UserProfile.objects.create(user=instance, **profile_data)
                instance.profile = new_profile

        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length = 8)
    class Meta:
        model = User
        fields = ("email","password")
    def validate_password(self, value):
        validate_password(value);
        return value
    
    def create(self,validated):
        pwd = validated.pop("password")
        user = User.objects.create_user(**validated)
        user.set_password(pwd)
        user.save(update_fields=["password"])
        return user

class UserChangePassword(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['old_password']==attrs['new_password']:
            raise serializers.ValidationError("New password should be different from old password")
        validate_password(attrs['new_password'])
        return super().validate(attrs)

class UserEmailSerializer(serializers.Serializer):
    email= serializers.EmailField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        validate_password(attrs['new_password'])
        return super().validate(attrs)

        
#Costom claims --> constom payload data        
class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        t = super().get_token(user)
        t["role"]=user.role
        t["email"]= user.email
        t["is_email_verified"] = user.is_email_verified
        return t