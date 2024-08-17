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
        
        otp=generate_otp()
        user_profile , created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone':phone,'otp':otp , 'otp_generated_at': timezone.now()}
            )
        send_otp_via_email(user.email,otp)
        return user
    

class OTPVerificationSerializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=4)

    def validate(self,data):
        email=data.get('email')
        print('this is called first',email)
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
        print('this',user_profile.otp)
        if user_profile.otp != otp:
            raise serializers.ValidationError("Invalid OTP")
        return data
    
    def save(self):
        email = self.validated_data['email']
        user=CustomUser.objects.get(email=email)
        user_profile = user.User_profile
        print("what is this",user_profile)
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
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
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
    profile_picture = serializers.ImageField(source='User_profile.profile_picture',read_only=True)

    class Meta:
        model=CustomUser
        fields =['username','profile_picture']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.EmailField(source ='user.email',read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username','email','address','pincode','phone','alternative_phone','profile_picture']
    

class EditUserProfileSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(source='user.email')
    username=serializers.CharField(source='user.username')
    address=serializers.CharField(required=False)
    phone=serializers.CharField(required=True)
    alternative_phone=serializers.CharField(required=False)
    pincode=serializers.CharField(required=False)
    profile_picture=serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields= ['username','email','address','phone','alternative_phone','pincode','profile_picture']

    def validate_username(self,value):
        if ' ' in value or not value.isalpha():
            raise serializers.ValidationError("The Username should only contain alphabets and no spaces.")
        return value
    
    def validate_address(self,value):
        if value and (value[0].isspace() or any(c in "!@#$%^&()_+=<>?/;:'\"[]{}|\\`~" for c in value)and not ('.' in value or ',' in value)):
            raise serializers.ValidationError("Address cannot start with a space or contain special character except dot(.) and comma (,)")
        return value
    
    def validate_phone(self,value):
        if not value.isdigit() or len(value)!=10:
            raise serializers.ValidationError("Phone number must be 10 digits.")
        return value
    
    def validate_alternative_phone(self,value):
        if value and ( not value.isdigit() or len(value) !=10):
            raise serializers.ValidationError("Alternative phone number must be 10 digits.")
        if value == self.initial_data.get('phone'):
            raise serializers.ValidationError('Alternative phone number cannot be the same as the primary phone number.')
        return value
    
    
    def validate_pincode(self,value):
        if not value.isdigit() or len(value) !=6:
            raise serializers.ValidationError("Pincode must be 6 digits.")
        return value
    
    def validate_profile_picture(self, value):
        # Example validation: Check the size of the image (max 2MB)
        max_size = 2 * 1024 * 1024  # 2MB
        if value and value.size > max_size:
            raise serializers.ValidationError("Profile picture size cannot exceed 2MB.")
        # You can also add other validations like checking file type if necessary
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
        products = Product.objects.filter(category=category)
        return ProductSerializer(products, many=True).data
    



class FetchProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id']

class CollectionRequestSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    class Meta:
        model = CollectionRequest
        fields = ['shop', 'date_requested', 'name', 'address', 'landmark', 'pincode', 'phone', 'upi','products']

     
    def create(self, validated_data):
        product_ids = validated_data.pop('products',[])
        print("Product IDs:", product_ids)
        print("Validated Data:", validated_data)  # Log validated data
        if not isinstance(product_ids, list) or not product_ids:
            raise serializers.ValidationError({"products": "This field is required."})
        user = self.context['request'].user
        collection_request = CollectionRequest.objects.create(user=user,**validated_data)
        products = Product.objects.filter(id__in=product_ids)
        collection_request.products.set(products)
        return collection_request

    
# class ScrapCollectionRequestSerializer(serializers.ModelSerializer):
#     date_requested = serializers.DateField() 
#     name = serializers.CharField()
#     address = serializers.CharField()
#     landmark = serializers.CharField()
#     pincode = serializers.CharField()
#     phone = serializers.CharField()
#     upi = serializers.CharField()
#     products = serializers.ListField(child=serializers.IntegerField(), write_only=True)

#     class Meta:
#         model = CollectionRequest
#         fields = ['date_requested', 'name', 'address', 'landmark', 'pincode', 'phone', 'upi','products']

#     def validate(self, data):
#         print('validating data',data)
#         for field in ['date_requested', 'name', 'address', 'landmark', 'pincode', 'phone', 'upi','products','shop']:
#             if not data.get(field):
#                 raise serializers.ValidationError({field: "This field is required."})
#         return data

#     def validate_date_requested(self, value):
#         today = date.today()
#         if value < today or value > today + timedelta(days=7):
#             raise serializers.ValidationError("The date should be within the current day or within a week (no dates before today or after 7 days).")
#         return value

#     def validate_name(self, value):
#         if not value.isalpha():
#             raise serializers.ValidationError("The name can only contain alphabets and no spaces.")
#         return value

#     def validate_address(self, value):
#         if value and (value[0].isspace() or any(c in "!@#$%^&()_+=<>?/;:'\"[]{}|\\`~" for c in value) and not ('.' in value or ',' in value)):
#             raise serializers.ValidationError("Address cannot start with a space or contain special characters except dot (.) and comma (,).")
#         return value

#     def validate_landmark(self, value):
#         if not value.isalpha():
#             raise serializers.ValidationError("The landmark can only contain alphabets and no spaces.")
#         return value

#     def validate_pincode(self, value):
#         if not value.isdigit() or len(value) != 6:
#             raise serializers.ValidationError("The pincode must be a 6-digit number.")
#         return value

#     def validate_phone(self, value):
#         if not value.isdigit() or len(value) != 10:
#             raise serializers.ValidationError("The phone number should be a 10-digit number.")
#         return value

#     def validate_upi(self, value):
#         if " " in value or '@' not in value:
#             raise serializers.ValidationError("The UPI ID should not contain spaces and must include '@'.")
#         return value
    
#     def create(self, validated_data):
#         products = validated_data.pop('products',[])
#         collection_request = CollectionRequest.objects.create(**validated_data)
#         for product_id in products:
#             product = Product.objects.get(id=product_id)
#             collection_request.products.add(product)
#         return collection_request
        
        
        