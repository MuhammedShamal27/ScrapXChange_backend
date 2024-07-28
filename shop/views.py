from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from . serializer import *
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated

# Create your views here.


class ShopRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = ShopRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Shop registration request submitted successfully. Awaiting admin approval."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    