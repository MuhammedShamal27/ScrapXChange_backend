from django.db import IntegrityError
from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .generate_otp import *
from django.core.validators import RegexValidator
from django.utils import timezone
import datetime
from shop.models import *
from datetime import date,timedelta
from scrapxchange_admin.models import *
from . tasks import *

class UserProfilePhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields = ['phone']

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields = ["email", "username" ,"phone", "password", "confirm_password"]
        extra_kwargs = {
            'password':{'write_only':True},
        }

    def validate_username(self,value):
        if ' ' in value:
            raise serializers.ValidationError("The Username can't contain space")
        if not value.isalpha():
            raise serializers.ValidationError("Username should only contain alphabets.")
        if CustomUser.objects.filter(username=value).exclude(User_profile__is_validated=False).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exclude(User_profile__is_validated=False).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone(self,value):
        if not value.isdigit():
            raise serializers.ValidationError('The phone should only contain number')
        if len(value)!=10:
            raise serializers.ValidationError("The phone number should be 10 digit")
        if UserProfile.objects.filter(phone=value).exclude(is_validated=False).exists():
            raise serializers.ValidationError("A user with this phone number is already exists.")
        return value

    def validate_password(self,value):
        if ' ' in value:
            raise serializers.ValidationError("Password should not conatin spaces.")
        if len(value) < 8 or len(value) > 17:
            raise serializers.ValidationError("The password must be between min 8 and max 15 character.")
        return value
    
    def validate(self,data):
        if data['password'] !=data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        phone = validated_data.pop('phone')
        validated_data.pop('confirm_password')
        try:
            user=CustomUser.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],
                password=validated_data['password'],
            )
        except IntegrityError:
            raise serializers.ValidationError("A user with this email already exists.")
        
        user_profile , created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone':phone}
            )
        return user
    

class OTPVerificationSerializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=4)

    def validate(self,data):
        email=data.get('email')
        otp=data.get('otp')

        if not email or not otp:
            raise serializers.ValidationError("Email and OTP are required")
        try:
            user=CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        if not hasattr(user,'User_profile'):
            raise serializers.ValidationError("No associated UserProfile found for this User.")
        
        user_profile = user.User_profile
        
        if user_profile.otp_generated_at and(timezone.now() - user_profile.otp_generated_at > datetime.timedelta(minutes = 1)):
            raise serializers.ValidationError("OTP has expired , Please request for new one")
        if user_profile.otp != otp:
            raise serializers.ValidationError("Invalid OTP")
        return data
    
    def save(self):
        email = self.validated_data['email']
        user=CustomUser.objects.get(email=email)
        user_profile = user.User_profile
        user.is_active=True
        user_profile.otp=""
        user_profile.otp_generated_at = None
        user_profile.save()
        user.save()
        return user
    
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self,value):
        try:
            user = CustomUser.objects.get(email=value)
            user_profile =UserProfile.objects.get(user=user)
            if user.is_active:
                raise serializers.ValidationError('User is already active.')
            self.context['user_profile'] = user_profile

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User profile not found.")
        return value
    
class PasswordRestRequestSerializer(serializers.Serializer):
    email=serializers.EmailField()
    
    def validate_email(self,value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
class EmailOTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    
    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            user = CustomUser.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User profile not found.")
        
        if user_profile.otp !=otp:
            raise serializers.ValidationError("Invalid OTP.")
        
        return data
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password =serializers.CharField(write_only=True,min_length=8,max_length=15)

    def validate(self,data):
        email= data.get('email')
        new_password = data.get('new_password')
        print('new_password')

        try:
            user = CustomUser.objects.get(email=email)
    
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        if len(new_password)<8 or len(new_password) >17:
            raise serializers.ValidationError('The Password should be min 8 and max 17 character.')
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user=CustomUser.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)

    def validate(self,data):
        email=data.get('email')
        print("email:",email)
        password=data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        try:
            user = CustomUser.objects.get(email=email)
            user_profile=UserProfile.objects.get(user=user)
            
            if user_profile.is_blocked:
                raise serializers.ValidationError("This user is blocked.")

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')

        if user is None:
            raise serializers.ValidationError("Invalid emai or password")
        
        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password.')
        
        refresh = RefreshToken.for_user(user)

        return {
            'email': user.email,
            'username':user.username,
            'tokens':{
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }


class HomePageSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(source='User_profile.profile_picture',read_only=True)

    class Meta:
        model=CustomUser
        fields =['id','username','profile_picture']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.EmailField(source ='user.email',read_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.profile_picture:
            profile_picture_url = instance.profile_picture  
            if not profile_picture_url.startswith("http"):
                profile_picture_url = f"https://res.cloudinary.com/dqffglvoq/{profile_picture_url}"
            data['profile_picture'] = profile_picture_url
        return data

    class Meta:
        model = UserProfile
        fields = ['username','email','address','pincode','phone','alternative_phone','profile_picture']
    
class EditUserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    address = serializers.CharField(required=False)
    phone = serializers.CharField(required=True)
    alternative_phone = serializers.CharField(required=False)
    pincode = serializers.CharField(required=False)
    profile_picture = serializers.CharField(required=False)  

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'address', 'phone', 'alternative_phone', 'pincode', 'profile_picture']

    def validate_username(self, value):
        if ' ' in value or not value.isalpha():
            raise serializers.ValidationError("The Username should only contain alphabets and no spaces.")
        return value

    def validate_address(self, value):
        if value and (value[0].isspace() or any(c in "!@#$%^&()_+=<>?/;:'\"[]{}|\\`~" for c in value) and not ('.' in value or ',' in value)):
            raise serializers.ValidationError("Address cannot start with a space or contain special characters except dot(.) and comma (,).")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits.")
        return value

    def validate_alternative_phone(self, value):
        if value and (not value.isdigit() or len(value) != 10):
            raise serializers.ValidationError("Alternative phone number must be 10 digits.")
        if value == self.initial_data.get('phone'):
            raise serializers.ValidationError('Alternative phone number cannot be the same as the primary phone number.')
        return value

    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("Pincode must be 6 digits.")
        return value

    def validate_profile_picture(self, value):
        """
        Validates that the profile picture is either a valid URL or a file upload.
        """
        max_size = 2 * 1024 * 1024  # 2MB
        if value:
            if isinstance(value, str) and not value.startswith("http"):
                raise serializers.ValidationError("Profile picture must be a valid URL or an uploaded file.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        if 'username' in user_data:
            user.username = user_data['username']
        if 'email' in user_data:
            user.email = user_data['email']
        user.save()

        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.alternative_phone = validated_data.get('alternative_phone', instance.alternative_phone)
        instance.pincode = validated_data.get('pincode', instance.pincode)
        
        profile_picture = validated_data.get('profile_picture')
        if profile_picture:
            if isinstance(profile_picture, str) and profile_picture.startswith("http"):
                instance.profile_picture = profile_picture
            else:
                instance.profile_picture = profile_picture
        
        instance.save()
        return instance

    
class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'shop_name', 'address', 'place', 'profile_picture']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'image']

class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products']

    def get_products(self, category):
        print('comming')
        products = Product.objects.filter(category=category)
        print('the products',products)
        print(f"Category: {category.name}, Products: {products}")
        return ProductSerializer(products, many=True).data
    

class CollectionRequestSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)

    class Meta:
        model = CollectionRequest
        fields = ['shop', 'date_requested', 'name', 'address', 'landmark', 'pincode', 'phone', 'upi', 'products','add_note']
        
    def to_internal_value(self, data):
        data = data.copy()
        # products_data = data.getlist('products[]') if not working change to this and comment the below one.
        products_data = data.get('products', [])
        print('the internal value',products_data)
        if products_data:
            # data.setlist('products', products_data) if not working change to this and comment the below one.
            data['products'] = products_data
        return super().to_internal_value(data)
    
    def validate_date_requested(self, value):
        today = date.today()
        if value < today or value > today + timedelta(days=7):
            raise serializers.ValidationError("The date should be within the current day or within a week (no dates before today or after 7 days).")
        return value

    def validate_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("The name can only contain alphabets and no spaces.")
        return value

    def validate_address(self, value):
        if value and (value[0].isspace() or any(c in "!@#$%^&()_+=<>?/;:'\"[]{}|\\`~" for c in value) and not ('.' in value or ',' in value)):
            raise serializers.ValidationError("Address cannot start with a space or contain special characters except dot (.) and comma (,).")
        return value

    def validate_landmark(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("The landmark can only contain alphabets and no spaces.")
        return value

    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("The pincode must be a 6-digit number.")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("The phone number should be a 10-digit number.")
        return value

    def validate_upi(self, value):
        if " " in value or '@' not in value:
            raise serializers.ValidationError("The UPI ID should not contain spaces and must include '@'.")
        return value

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        print('before products data',products_data)
        scrap_request = CollectionRequest.objects.create(**validated_data)
        print('after products data',products_data)
        for products_id in products_data:
            scrap_request.products.add(products_id)
        return scrap_request


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields ='__all__'
        
# ---------- Shops Listing In UserSide ------------------

class ShopListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    is_active = serializers.BooleanField(source='user.is_active')
    products = ProductSerializer(source='user.products', many=True)
    
    class Meta:
        model = Shop
        fields =['id', 'shop_name', 'email', 'username', 'is_active', 'address', 'state', 'district','latitude','longitude','products','user_id']
        
class FetchLastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'timestamp', 'message']

        
class ChatRoomSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    # messages = serializers.SerializerMethodField()
    user = HomePageSerializer()
    
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user', 'shop', 'created_at']
        
    # def get_messages(self, obj):
    #     messages = Message.objects.filter(room=obj)
    #     return FetchLastMessageSerializer(messages, many=True).data
        
    def create(self, validated_data):
        
        room, created = ChatRoom.objects.get_or_create(
            user=validated_data['user'],
            shop=validated_data['shop'],
        )
        return room

class MessageSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False)
    video = serializers.CharField(required=False)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'receiver', 'timestamp', 'message','image','video']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            print('image')
            data['image'] = instance.image

        if instance.video:
            print('video')
            data['video'] = instance.video  


        return data
    
    def create(self, validated_data):
        
        print('the validated data',validated_data)
        room = validated_data['room']
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        
        if sender != room.user and sender != room.shop.user:
            raise serializers.ValidationError("Sender is not part of this chat room.")
        
        if receiver != room.user and receiver != room.shop.user:
            raise serializers.ValidationError("Receiver is not part of this chat room.")
        
        return super().create(validated_data)



class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['receiver', 'reason' ,'description']
        
    def validate(self, data):
        if data['reason'] == 'other' and not data.get('description'):
            raise serializers.ValidationError("Description is required when reason is other.")
        return data

    def create(self, validated_data):
        # Set the sender to the currently authenticated user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
    

class TransactionProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = TransactionProduct
        fields = ['product_name', 'quantity']

class TransactionSerializer(serializers.ModelSerializer):
    products = TransactionProductSerializer(source='transaction_products', many=True, read_only=True)
    shop_name = serializers.CharField(source='collection_request.shop.shop_name', read_only=True)
    user_email = serializers.CharField(source='collection_request.user.email', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'user_email', 'shop_name', 'total_quantity', 'total_price', 'date_picked', 'payment_method', 'products']
        

class UserNotificationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = ['id' , 'sender' , 'receiver' ,'message' ,'is_read' ,'created_at','notification_type']
    

# Serializer for Collection Requests
class RequestCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['id', 'scheduled_date', 'address', 'phone', 'is_collected','shop', 
                  'date_requested', 'name', 'landmark', 'pincode', 'phone', 'upi','add_note']

# Serializer for Dashboard Data
class DashboardSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)
    pending_pickups = RequestCollectionSerializer(many=True)
    total_collections = RequestCollectionSerializer(many=True)
    total_collected_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    today_pending_pickups = RequestCollectionSerializer(many=True)
    pending_requests = RequestCollectionSerializer(many=True)