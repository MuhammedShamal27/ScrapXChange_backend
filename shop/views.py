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
        return Category.objects.filter(shop=self.request.user)

@method_decorator(csrf_exempt,name='dispatch') 

class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.shop.is_verified==True:
            raise PermissionDenied("Your shop is not verified.")
        serializer.save(shop = user)
        
class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        # The following checks are handled by the serializer:
        # - Whether the shop exists and belongs to the user
        # - Whether the shop is verified and the user is a shop owner
        
        category = self.get_object()

        # Check if the category belongs to the user
        if category.shop != user:
            raise PermissionDenied("You do not have permission to edit this category.")
        
        # Save the serializer if all checks pass
        serializer.save()

# class CategoryUpdateView(generics.UpdateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategoryUpdateSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def perform_update(self, serializer):
#         user =self.request.user
#         print("the user",user)

#         try:
#             shop =Shop.objects.get(user=user)
#             print("the shop",shop)
#         except Shop.DoesNotExist:
#             raise PermissionDenied("Shop assoiciated with the user does  not exist.")
        
#         category = self.get_object()
#         print("this is the category",category)
#         print("this is the category shop",category.shop)

#         if category.shop !=user:
#             raise PermissionDenied("You do not have permission to edit this category.")
        
#         if not shop.is_verified==True or not user.is_shop==True:
#             raise PermissionDenied("Only verified shops can edit categories.")
        
#         serializer.save()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise PermissionDenied("Shop associated with this user does not exist.")
        
        return Product.objects.filter(shop=user)
    

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
        
        serializer.save(shop=user)


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
        if product.shop != user:
            raise PermissionDenied("You do not have permission to edit this product.")
        
        if not shop.is_verified:
            raise PermissionDenied("Only Verified shops can update products.")
        
        serializer.save()