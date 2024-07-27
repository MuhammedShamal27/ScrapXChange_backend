from rest_framework import serializers
from user.models import CustomUser
from . models import *


class ShopRegisterSerializer(serializers.ModelSerializer):
    username=serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
    password=serializers.CharField(write_only=True)
    re_enter_password=serializers.CharField(write_only=True)
    shop_name=serializers.CharField(required=True)
    shop_license_number=serializers.CharField(required=True)
    address=serializers.CharField(required=True)
    place=serializers.CharField(required=True)
    phone=serializers.CharField(required=True)

    class Meta:
        model = Shop
        fields =['username','email','password','re_enter_password','shop_name','shop_license_number','address','place','phone']

    def validate_username(self,data)

    def validate(self,data):
        if data['password']!=data['re_enter_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    