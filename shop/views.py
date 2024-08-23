from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from . serializer import *
from rest_framework import status,generics,permissions
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.


class ShopRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = ShopRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Shop registration request submitted successfully. Awaiting admin approval."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ShopLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = ShopLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ShopHomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user=request.user
        serializer = ShopHomeSerializer(user)
        return Response(serializer.data)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_shop:
            raise PermissionDenied("You do not have permission to access this resource.")
        print('the user',self.request.user)
        return Category.objects.filter(user=self.request.user)
    


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user
        if not user.shop.is_verified:
            raise PermissionDenied("Your shop is not verified.")
        serializer.save(user=user)

        
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        category = super().get_object()
        print('category user',category,category.user,)
        if category.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this category.")
        return category
        
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user
        
        category = self.get_object()
        print('category user',category,category.user,user)
        if category.user != user:
            raise PermissionDenied("You do not have permission to edit this category.")
        serializer.save()

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(user)
        try:
            
            shop = Shop.objects.get(user=user)
            print('the user i get',user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        return Product.objects.filter(user=shop.user)
    

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        if not shop.is_verified==True:
            raise PermissionDenied("Only verified shops can create products.")
        
        serializer.save(user=user)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        product = super().get_object()
        if product.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this product.")
        return product


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        product = self.get_object()
        if product.user != user:
            raise PermissionDenied("You do not have permission to edit this product.")
        
        if not shop.is_verified:
            raise PermissionDenied("Only Verified shops can update products.")
        
        serializer.save()
        
class ScrapRequestListView(generics.ListAPIView):
    serializer_class = ScrapRequestListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        shop = self.request.user.shop
        if not shop:
            return CollectionRequest.objects.none()
        print('this is the shop name',shop)
        return CollectionRequest.objects.filter(shop=shop , is_accepted=False , is_rejected=False , is_scheduled=False)

    
        
class ScrapRequestDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class=ScrapRequestListSerializer
    lookup_field ='pk'
    
    def get(self,request,pk, *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request = CollectionRequest.objects.get(pk=pk, shop=request.user.shop)
            serializer = self.serializer_class(scrap_request)
            return Response(serializer.data)
        except CollectionRequest.DoesNotExist:
            return Response({"error": "Scrap request not found."}, status=404)
        
        
class ScheduleRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SheduleSerializer
    
    def post(self,request,pk , *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request= CollectionRequest.objects.get(pk=pk , shop=request.user.shop)
            serializer = self.serializer_class(scrap_request,data=request.data,context={'request':request})
            if not serializer.is_valid():
                print(serializer.errors)  
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            scrap_request.is_scheduled = True
            scrap_request.scheduled_date = scrap_request.date_requested
            scrap_request.save()
            return Response({'message':'Request shedule succesfully'})
        except CollectionRequest.DoesNotExist:
            return Response({"error":"Scrap request not found."},status=status.HTTP_404_NOT_FOUND)        
            
class RescheduleRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RescheduleSerializer

    def post(self, request, pk, *args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')

        try:
            scrap_request = CollectionRequest.objects.get(pk=pk, shop=request.user.shop)
        except CollectionRequest.DoesNotExist:
            return Response({"error": "Scrap request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(scrap_request, data=request.data, partial=True, context={'request': request})
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Request rescheduled successfully'})
    
class RejectRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ScrapRequestListSerializer
    
    def post(self,request,pk,*args, **kwargs):
        if not self.request.user.is_shop:
            raise PermissionDenied('Access to this page is only for the verified shop.')
        try:
            scrap_request = CollectionRequest.objects.get(pk=pk , shop=request.user.shop)
            scrap_request.is_rejected=True
            scrap_request.reject_message=request.data.get('reason','')
            scrap_request.save()
            return Response({'message':'Request has rejected.'})
        except CollectionRequest.DoesNotExist:
            return Response({'error':'Scrap request not found.'},status=status.HTTP_404_NOT_FOUND)
        
