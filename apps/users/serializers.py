from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "role", "is_email_verified", "date_joined", "last_login")
        read_only_field = ("id","role","is_email_verified","date_joined", "last_login")

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("full_name",)
        
    def validate_full_name(self, value):
        if not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError("Only Letter allowed")
        return value
    
    
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
        

        
#Costom claims --> constom payload data        
class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        t = super().get_token(user)
        t["role"]=user.role
        t["email"]= user.email
        t["is_email_verified"] = user.is_email_verified
        return t