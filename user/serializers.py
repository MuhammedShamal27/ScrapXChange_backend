from .models import CustomUser,UserProfile
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .generate_otp import *
from django.core.validators import RegexValidator


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
        return value
    
    def validate_phone(self,value):
        if not value.isdigit():
            raise serializers.ValidationErrorf('The phone should only contain number')
        if len(value)!=10:
            raise serializers.ValidationError("The phone number should be 10 digit")
        if UserProfile.objects.filter(phone=value).exists():
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
        user=CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        
        otp=generate_otp()
        user_profile,created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'phone':phone,'otp':otp}
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
    
class PasswordRestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)
    new_password =serializers.CharField(write_only=True,min_length=8)

    def validate(self,data):
        email= data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')

        try:
            user = CustomUser.objects.get(email=email)
            user_profile=UserProfile.objects.get(user=user)
            if user_profile.otp != otp:
                raise serializers.ValidationError('Invalid OTP.')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        if len(new_password)<8 or len(new_password) >17:
            raise serializers.ValidationError('The Password should be min 8 and max 15 character.')
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user=CustomUser.objects.get(email=email)
        user_profile=UserProfile.objects.get(user=user)
        user.set_password(new_password)
        user_profile.otp=""
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
        if value and (value[0].isspace() or any(c in "!@#$%^&()_+=<>?/;:'\"[]{}|\\`~" for c in value)):
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
    
    def update(self,instance,validate_data):
        user_data = validate_data.pop('user',{})
        user = instance.user
        user.username = user_data.get('username',user.username)
        user.email = validate_data.get('email',user.email)
        user.save()
        
        instance.address = validate_data.get('address',instance.address)
        instance.phone = validate_data.get('phone',instance.phone)
        instance.alternative_phone = validate_data.get('alternative_phone',instance.alternative_phone)
        instance.pincode = validate_data.get('pincode',instance.pincode)
        instance.profile_picture = validate_data.get('profile_picture',instance.profile_picture)
        instance.save()
        return instance