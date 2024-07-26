from .models import CustomUser,UserProfile
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields = ["email", "username" , "password"]
    
    def create(self, validated_data):
        user=CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model =UserProfile
        fields =['address','pincode','phone','alternative_phone','profile_picture']


class OTPVerificationSerializer(serializers.ModelSerializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)

    def validate(self,data):
        email=data.get('email')
        otp=data.get('otp')

        if not email or not otp:
            raise serializers.ValidationError("Email and OTP are required")
        try:
            user=CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        if user.otp !=otp:
            raise serializers.ValidationError("Invalid OTP")
        return data
    
    def save(self):
        email = self.validated_data['email']
        user=CustomUser.objects.get(email=email)
        user.is_active=True
        user.otp=""
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username','email']