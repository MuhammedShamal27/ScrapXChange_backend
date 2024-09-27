from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions,generics,serializers
from rest_framework.exceptions import PermissionDenied,NotFound
from . serializer import *
from django.contrib.auth import login
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from user.models import CustomUser
from rest_framework.generics import RetrieveAPIView
# Create your views here.


class AdminLoginView(APIView):
    permission_classes =[AllowAny]


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
        queryset = CustomUser.objects.filter(is_superuser=False, is_shop=False)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
            
        return queryset

    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)
    
class BlockedUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(is_superuser=False, is_shop=False, User_profile__is_blocked=True)

class UnblockedUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(is_superuser=False, is_shop=False, User_profile__is_blocked=False)

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
            
            actionPerformed =request.data.get('actionPerformed')
            if actionPerformed =='block':
                user_profile.is_blocked = True
                message ='User has been blocked.'
            elif actionPerformed =='unblock':
                user_profile.is_blocked = False
                message = 'User has been unblocked.'
            else:
                return Response({"error":"Invalid action. Use 'block' or 'unblock'."},status=status.HTTP_400_BAD_REQUEST)
            user_profile.save()
            print("the messge",message)
            return Response({"message":message},status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error":"User profile not found."},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to acess this resource.")
        queryset = CustomUser.objects.filter(is_superuser=False,is_shop=True,shop__is_verified=True)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
            
        return queryset

    
    def list(self,request,*args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message":'No shops have been verified by the admin.'})
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)
    
class BlockedShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(is_superuser=False, is_shop=True, shop__is_blocked=True, shop__is_verified=True)

class UnblockedShopListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(is_superuser=False, is_shop=True, shop__is_blocked=False, shop__is_verified=True)

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
    
    def post(self, request, id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=id)
            if not request.user.is_superuser:
                raise PermissionDenied("You do not have permission to modify this shop.")
            
            if not hasattr(user, 'shop'):
                return Response({"error": "Shop associated with this user not found."}, status=status.HTTP_404_NOT_FOUND)
            
            shop = user.shop

            actionPerformed = request.data.get('actionPerformed')
            if actionPerformed == 'block':
                shop.is_blocked = True
                message = 'Shop has been blocked.'
            elif actionPerformed == 'unblock':
                shop.is_blocked = False
                message = 'Shop has been unblocked.'
            else:
                return Response({"error": "Invalid action. Use 'block' or 'unblock'."}, status=status.HTTP_400_BAD_REQUEST)
            
            shop.save()
            return Response({"message": message}, status=status.HTTP_200_OK)
        
        except Shop.DoesNotExist:
            return Response({"error": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ShopRequestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ShopListSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(shop__is_verified=False,shop__is_rejected=False)
    
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
            raise PermissionDenied("You do not have permission to access this resource.")
        return CustomUser.objects.filter(shop__is_verified=False)
    
    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {self.lookup_field: self.kwargs['id']}
        obj = queryset.filter(**filter_kwargs).first()
        if not obj:
            raise NotFound("Shop not found.")
        return obj

    

class AcceptShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        try:
            user = CustomUser.objects.get(id=id)
            shop = user.shop
            shop.is_verified = True
            shop.save()
            return Response({"message": 'Shop has been verified.'})
        except CustomUser.DoesNotExist:
            raise NotFound("User not found.")
        except Shop.DoesNotExist:
            raise NotFound("Shop not found.")
        
class RejectShopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        try:
            user = CustomUser.objects.get(id=id)
            shop = user.shop
            shop.is_rejected = True
            shop.save()
            return Response({"message": 'Shop has been rejected.'})
        except CustomUser.DoesNotExist:
            raise NotFound("User not found.")
        except Shop.DoesNotExist:
            raise NotFound("Shop not found.")
        
        
class ReportView(generics.ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.exclude(is_checked=True)



class ReportBlockUnblockView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request,id):
        # Try to fetch UserProfile first
        print('the request data',request.data)
        try:
            user_profile = UserProfile.objects.get(user__id=id)
            serializer = UserProfileBlockUnblockSerializer(user_profile, data=request.data, partial=True)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Try to fetch Shop if UserProfile does not exist
        if not user_profile:
            try:
                shop = Shop.objects.get(user__id=id)
                serializer = ShopBlockUnblockSerializer(shop, data=request.data, partial=True)
            except Shop.DoesNotExist:
                return Response({"error": "User or shop not found."}, status=404)

        # Perform the update
        if serializer.is_valid():
            updated_instance = serializer.save()
            status = "blocked" if updated_instance.is_blocked else "unblocked"
            
            report_id=request.data.get('reportId')
            # Fetch and update the report associated with this user
            report = Report.objects.get(id=report_id)  # Get the report with the receiver
            if report:
                report.is_checked = True  # Set is_checked to False
                report.save()
                
            return Response({"message": f"{updated_instance.user.username} has been {status} successfully."})

        return Response(serializer.errors, status=400)
    
    
class DashboardDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all users excluding shops
        users = CustomUser.objects.filter(is_shop=False, is_superuser=False)
        total_users = users.count()

        # Get all shops
        shops = Shop.objects.all()
        total_shops = shops.count()

        # Get all collection requests
        collection_requests = CollectionRequest.objects.all()
        total_collection_requests = collection_requests.count()

        # Get all unverified shops
        unverified_shops = Shop.objects.filter(is_verified=False)
        total_unverified_shops = unverified_shops.count()

        # Serialize the data
        user_serializer = UserSerializer(users, many=True)
        shop_serializer = ShopSerializer(shops, many=True)
        collection_request_serializer = CollectionRequestSerializer(collection_requests, many=True)
        unverified_shop_serializer = ShopSerializer(unverified_shops, many=True)

        data = {
            'users': user_serializer.data,
            'total_users': total_users,
            'shops': shop_serializer.data,
            'total_shops': total_shops,
            'collection_requests': collection_request_serializer.data,
            'total_collection_requests': total_collection_requests,
            'unverified_shops': unverified_shop_serializer.data,
            'total_unverified_shops': total_unverified_shops,
        }

        return Response(data)