from django.shortcuts import get_object_or_404, render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .generate_otp import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.exceptions import NotFound
import logging
from rest_framework import generics

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
        serializer =EditUserProfileSerializer(user_profile)
        print('this is the get method',serializer)
        return Response(serializer.data)

    def put(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_404_NOT_FOUND)
        print(request.data.get('profile_picture'))
        if isinstance(request.data.get('profile_picture'), str):
            request_data = request.data.copy()
            request_data.pop('profile_picture', None)
            serializer = EditUserProfileSerializer(user_profile, data=request_data, partial=True)
        else:
            serializer = EditUserProfileSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
class ShopListView(ListAPIView):
    serializer_class = ShopSerializer

    def get_queryset(self):
        return Shop.objects.filter(
            user__is_superuser=False, 
            user__is_shop=True, 
            is_blocked=False, 
            is_verified=True, 
            is_rejected=False
        )


class ShopProductListView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        shop_id = self.kwargs.get('shop_id')
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            raise NotFound(detail="Shop not found")
        user = shop.user
        return Category.objects.filter(user=user).distinct()


  
class ScrapCollectionRequestView(APIView):
    def post(self, request):
        serializer = CollectionRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Handle the valid data (e.g., save to the database)
            return Response({"success": "Scrap collection request submitted"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# class ScrapCollectionRequestView(APIView):
#     permission_classes=[IsAuthenticated]

#     def post(self, request):
#         print('Incoming request data',request.data)
#         serializer = ScrapCollectionRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             print('the serilaizer error',serializer.errors)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)