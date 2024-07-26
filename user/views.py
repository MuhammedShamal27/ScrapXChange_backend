from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny


# Create your views here.

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        user_serializer=UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            return Response({'message':'User registered succesfully'},status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class OTPVerificationView(APIView):
    def post(self,request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            return Response({'message':'OTP Verified succesfully. User account activated'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        serializer=UserSerializer(user)
        return Response(serializer.data)