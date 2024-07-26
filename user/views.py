from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .generate_otp import *
from rest_framework.permissions import IsAuthenticated,AllowAny


# Create your views here.

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        user_serializer=UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'message':'User registered succesfully'},status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            return Response({'message':'OTP Verified succesfully. User account activated'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    def post(self,request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validate_data['email']
            user = CustomUser.objects.get(email=email)
            otp=generate_otp()
            user.otp=otp
            user.save()
            send_otp_via_email(email,otp)
            return Response({'message':'OTP sent successfully.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class PasswordRestRequestView(APIView):
    def post(self,request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validate_email['email']
            user = CustomUser.objects.get(email=email)
            otp = generate_otp()
            user.otp = otp
            user.save()
            send_otp_via_email(email,otp)
            return Response({'message':'OTP sent for password reset.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetView(APIView):
    def post(self,request):
        serializer = PasswordRestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Password reset successful.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes =[IsAuthenticated]

    def get(self,request):
        profile = request.user.User_profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self,request):
        profile = request.user.User_profile
        serializer = UserProfileSerializer(profile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

