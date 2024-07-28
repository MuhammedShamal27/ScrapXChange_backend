from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions,generics,serializers
from rest_framework.exceptions import PermissionDenied,NotFound
from . serializer import *
from django.contrib.auth import login
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from user.models import CustomUser
from rest_framework.generics import RetrieveAPIView
# Create your views here.


class AdminLoginView(APIView):
    permission_classes =[IsAdminUser]


    def post(self,request,*args, **kwargs):
        serializer =AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh' : str(refresh),
                'access' : str(refresh.access_token),
            },status=status.HTTP_200_OK)  
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class AdminHomeView(APIView):
    permission_classes =[permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        serializer = AdminUserSerializer(request.user)
        return Response(serializer.data)
    

class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resources.")
        return CustomUser.objects.filter(is_superuser=False,is_shop=False)

    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

class UserDetailsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(is_superuser=False,is_shop=False)
    
class UserBlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post (self,request,id,*args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user_id=id)
            if not request.user.is_superuser:
                raise PermissionDenied("You do not have permission to modify this user.")
            
            action =request.data.get('action')
            if action =='block':
                user_profile.is_blocked = True
                message ='User has been blocked.'
            elif action =='unblock':
                user_profile.is_blocked = False
                message = 'User has been unblocked.'
            else:
                return Response({"error":"Invalid action. Use 'block' or 'unblock'."},status=status.HTTP_400_BAD_REQUEST)
            user_profile.save()
            return Response({"message":"User has been blocked."},status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error":"User profile not found."},status=status.HTTP_404_NOT_FOUND)



class ShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to acess this resource.")
        return CustomUser.objects.filter(is_superuser=False,is_shop=True,shop__is_verified=True)
    
    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message":'No shops have been verified by the admin.'})
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)
    
class ShopDetailsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopListSerializer
    lookup_field = 'id'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resources.")
        return CustomUser.objects.filter(shop__is_verified=True)

class ShopBlockView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request,id,action):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        try:
            shop = Shop.objects.get(id=id)
            if action =='block':
                shop.is_blocked = True
                message ='Shop has been blocked.'
            elif action =='unblock':
                shop.is_blocked = False
                message = 'Shop has been unblocked.'
            else:
                return Response({"error":"Invalid action."},status=400)
            shop.save()
            return Response({"message":message})
        except Shop.DoesNotExist:
            raise NotFound("Shop not found.")
        

class ShopRequestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(shop__is_verified=False)
    
    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message":'No shops have been verified by the admin.'})
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)

class ShopRequestDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopListSerializer
    lookup_field = 'id'

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resources.")
        return CustomUser.objects.filter(shop__is_verified=False)
    

class AcceptShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,id):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        try:
            shop = Shop.objects.get(id=id)
            shop.is_verified = True
            shop.save()
            return Response({"message":'Shop has been verified.'})
        except Shop.DoesNotExist:
            raise NotFound("Shop not found.")
        
class RejectShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,id):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        try:
            shop = Shop.objects.get(id=id)
            shop_user = shop.user
            shop.delete()
            shop_user.is_shop = False
            shop_user.save()
            return Response({"message":'Shop has been rejected and deleted.'})
        except Shop.DoesNotExist:
            raise NotFound("Shop not found.")

