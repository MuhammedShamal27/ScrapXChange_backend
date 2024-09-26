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
        
        
class ReportSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    sender_is_blocked = serializers.SerializerMethodField()  
    receiver_is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id','sender', 'receiver', 'reason', 'is_checked', 
                  'timestamp', 'sender_name', 'receiver_name' 
                  ,'sender_is_blocked', 'receiver_is_blocked']

    def get_sender_name(self, obj):
        # Check if the sender is a shop or a regular user
        if obj.sender.is_shop:
            return obj.sender.shop.shop_name  # Fetch shop name
        return obj.sender.username  # Fetch regular username

    def get_receiver_name(self, obj):
        # Check if the receiver is a shop or a regular user
        if obj.receiver.is_shop:
            return obj.receiver.shop.shop_name  # Fetch shop name
        return obj.receiver.username  # Fetch regular username
    
    def get_sender_is_blocked(self, obj):
        # Check if the sender is a shop or regular user and fetch the blocked status
        if obj.sender.is_shop:
            return obj.sender.shop.is_blocked  # Fetch block status for shop
        return obj.sender.User_profile.is_blocked  # Fetch block status for regular user

    def get_receiver_is_blocked(self, obj):
        # Check if the receiver is a shop or regular user and fetch the blocked status
        if obj.receiver.is_shop:
            return obj.receiver.shop.is_blocked  # Fetch block status for shop
        return obj.receiver.User_profile.is_blocked  
    
    
class UserProfileBlockUnblockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'is_blocked']

    def update(self, instance, validated_data):
        # Toggle the is_blocked field for UserProfile
        instance.is_blocked = not instance.is_blocked
        instance.save()
        return instance


class ShopBlockUnblockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'is_blocked']

    def update(self, instance, validated_data):
        # Toggle the is_blocked field for Shop
        instance.is_blocked = not instance.is_blocked
        instance.save()
        return instance
