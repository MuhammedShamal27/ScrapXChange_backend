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
    sender_warning_count = serializers.SerializerMethodField()
    receiver_warning_count = serializers.SerializerMethodField()
    

    class Meta:
        model = Report
        fields = ['id','sender', 'receiver', 'reason', 'description', 'is_checked', 
                  'timestamp', 'sender_name', 'receiver_name' 
                  ,'sender_is_blocked', 'receiver_is_blocked','receiver_warning_count','sender_warning_count']

    def get_sender_name(self, obj):
        if obj.sender.is_shop:
            return obj.sender.shop.shop_name  # Fetch shop name
        return obj.sender.username  # Fetch regular username

    def get_receiver_name(self, obj):
        if obj.receiver.is_shop:
            return obj.receiver.shop.shop_name  # Fetch shop name
        return obj.receiver.username  # Fetch regular username
    
    def get_sender_is_blocked(self, obj):
        if obj.sender.is_shop:
            return obj.sender.shop.is_blocked  # Fetch block status for shop
        return obj.sender.User_profile.is_blocked  # Fetch block status for regular user

    def get_receiver_is_blocked(self, obj):
        if obj.receiver.is_shop:
            return obj.receiver.shop.is_blocked  # Fetch block status for shop
        return obj.receiver.User_profile.is_blocked  
    
    def get_sender_warning_count(self, obj):
        if obj.sender.is_shop:
            return obj.sender.shop.warning_count  # Fetch block status for shop
        return obj.sender.User_profile.warning_count  # Fetch block status for regular user
    
    def get_receiver_warning_count(self, obj):
        if obj.receiver.is_shop:
            return obj.receiver.shop.warning_count  # Fetch block status for shop
        return obj.receiver.User_profile.warning_count  
    
    
class UserProfileBlockUnblockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'is_blocked', 'warning_count']

    def update(self, instance, validated_data):
        # Toggle block/unblock and handle warning increments
        if 'is_blocked' in validated_data:
            instance.is_blocked = validated_data['is_blocked']
        if 'warning_count' in validated_data:
            instance.warning_count = validated_data['warning_count']
        instance.save()
        return instance

class ShopBlockUnblockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'is_blocked', 'warning_count']

    def update(self, instance, validated_data):
        # Toggle block/unblock and handle warning increments
        if 'is_blocked' in validated_data:
            instance.is_blocked = validated_data['is_blocked']
        if 'warning_count' in validated_data:
            instance.warning_count = validated_data['warning_count']
        instance.save()
        return instance



class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(source='User_profile.profile_picture', read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'is_shop', 'is_superuser', 'date_joined', 'last_login', 'profile_picture']

class CollectionRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    shop = serializers.StringRelatedField()

    class Meta:
        model = CollectionRequest
        fields = ['id', 'user', 'shop', 'date_requested', 'scheduled_date', 'name', 
                  'address', 'landmark', 'pincode', 'phone', 'upi', 'products', 
                  'add_note', 'is_accepted', 'is_rejected', 'is_scheduled', 'is_collected']
        
class AllReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['sender', 'receiver', 'reason', 'description', 'is_checked', 'timestamp']
        
        
class AdminNotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['sender', 'receiver', 'message', 'is_read', 'created_at', 'notification_type', 'sender_name', 'receiver_name']

    # Method to get the sender's name
    def get_sender_name(self, obj):
        return obj.sender.username  # You can customize this to return any other field, like 'email'

    # Method to get the receiver's name
    def get_receiver_name(self, obj):
        return obj.receiver.username