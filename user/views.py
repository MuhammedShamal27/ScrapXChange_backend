from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .generate_otp import *
from rest_framework.permissions import IsAuthenticated,AllowAny
import logging

# Create your views here.

logger = logging.getLogger(__name__)
class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        logger.debug(f'Recieved data :{request.data}')
        user_serializer=UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            logger.info('valid data received , registering user...')
            user_serializer.save()
            logger.info('User registered successfully')
            
            return Response({'message':'User registered succesfully'},status=status.HTTP_201_CREATED)
        logger.warning(f'Invalid data :{user_serializer.errors}')
        return Response(user_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.save()
            refresh =RefreshToken.for_user(user)
            return Response({
                'message':'OTP Verified succesfully. User account activated',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },status=status.HTTP_200_OK)
        logger.warning(f'Invalid data :{serializer.errors}')
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            user_profile =UserProfile.objects.get(user=user)
            otp=generate_otp()
            user_profile.otp=otp
            user_profile.otp_generated_at = timezone.now()
            user_profile.save()
            send_otp_via_email(email,otp)
            return Response({'message':'OTP sent successfully.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class PasswordResetRequestView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            otp = generate_otp()
            user_profile.otp = otp
            user_profile.save()
            send_otp_via_email(email,otp)
            return Response({'message':'OTP sent for password reset.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class EmailOTPVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self ,request):
        serializer = EmailOTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            
            user_profile.otp =None
            user_profile.save()
            return Response({"message":"OTP verified successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class PasswordResetView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Password reset successful.'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        logger.info("userlogin",request.data)
        serializer = UserLoginSerializer(data=request.data)
        logger.info("the serilzier",serializer)
        if serializer.is_valid():
            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        logger.warning(f"serializer errors:{serializer.errors}")
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class HomePageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        logger.debug(f'Recieved data :{request.user}')
        user=request.user
        serializer = HomePageSerializer(user)
        logger.debug(f'Recieved data :{serializer.data}')
        return Response(serializer.data)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error":"UserProfile not found."},status=status.HTTP_404_NOT_FOUND)
        serializer =UserProfileSerializer(user_profile)
        return Response(serializer.data)

    

class EditUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            user_profile =UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error":"UserProfile not found."},status=status.HTTP_400_BAD_REQUEST)
        serializers =EditUserProfileSerializer(user_profile)
        return Response(serializers.data)

    def put(self,request):
        print(f"Authenticated user: {request.user}")
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error":"UserProfile not found."})

        serializer = EditUserProfileSerializer(user_profile,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Profile updated successfully','data':serializer.data},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)