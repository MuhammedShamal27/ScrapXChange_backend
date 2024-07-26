from .models import CustomUser,UserProfile
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .generate_otp import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)

    class Meta:
        model=CustomUser
        fields = ["email", "username" , "password", "confirm_password"]
        extra_kwargs = {
            'password':{'write_only':True},
        }

    def validate_username(self,value):
        if ' ' in value:
            raise serializers.ValidationError("The Username can't contain space")
        if not value.isalpha():
            raise serializers.ValidationError("Username should only contain alphabets.")
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
        validated_data.pop('confirm_password')
        user=CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        otp=generate_otp()
        user.otp=otp
        user.save()
        send_otp_via_email(user.email,otp)
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
        if user.otp !=otp:
            raise serializers.ValidationError("Invalid OTP")
        return data
    
    def save(self):
        email = self.validated_data['email']
        user=CustomUser.objects.get(email=email)
        user_profile = user.User_profile
        user.is_active=True
        user_profile.otp=""
        user_profile.save()
        user.save()
        return user
    
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self,value):
        try:
            user = CustomUser.objects.get(email=value)
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
    
class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password =serializers.CharField(write_only=True,min_length=6)

    def validate(self,data):
        email= data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')

        try:
            user = CustomUser.objects.get(email=email)
            if user.otp != otp:
                raise serializers.ValidationError('Invalid OTP.')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user=CustomUser.objects.get(email=email)
        user.set_password(new_password)
        user.otp=""
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(write_only=True)

    def validate(self,data):
        email=data.get('email')
        password=data.get('password')

        try:
            user = CustomUser.objects.get(email=email,password=password)

        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        if user is None:
            raise serializers.ValidationError("Invalid emai or password")
        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password.')
        
        return {
            'email': user.email,
            'username':user.username,
            'tokens':RefreshToken.for_user(user)
        }

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserProfile
        fields =['address','pincode','phone','alternative_phone','profile_picture']



