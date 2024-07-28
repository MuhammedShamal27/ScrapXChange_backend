from rest_framework import serializers
from django.contrib.auth import authenticate
from user.models import *
from shop.models import *
from .models import *


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email,password=password)
        if user and user.is_active and user.is_superuser:
            return user
        raise serializers.ValidationError("Invalid credentials or user is not authorized.")
    
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username','email']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserListSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='User_profile',read_only =True)
    class Meta:
        model =CustomUser
        fields =['id', 'email','username','is_active','user_profile']

class UserDetailSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='User_profile')
    class Meta:
        model = CustomUser
        fields = ['id','email','username','is_active','user_profile']

class UserBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['is_blocked']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields ='__all__'

class ShopListSerializer(serializers.ModelSerializer):
    shop= ShopSerializer()
    
    class Meta:
        model = CustomUser
        fields =['id','email','username','is_active','shop']