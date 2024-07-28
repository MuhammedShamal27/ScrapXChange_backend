from rest_framework import serializers
from user.models import CustomUser
from . models import *
import re


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


    def validate_username(self,value):
        if not value.isalpha():
            raise serializers.ValidationError("Username must cotain only alphabets.")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_shop_name(self,value):
        if not re.match(r'^[A-Za-z]+(?: [A-Za-z]+)*$',value):
            raise serializers.ValidationError("Shop name must conatin only alphabets and a single space between words,with no leading or trailing spaces.")
        return value
    
    def validate_shop_license_number(self,value):
        if not re.match(r'^[A-Z]{3}\d{11}$',value):
            raise serializers.ValidationError("Shop license number must start with uppercase alphabets followed by 11 digits.")
        if Shop.objects.filter(shop_license_number=value).exists():
            raise serializers.ValidationError("A shop with this license number already exists.")
        return value
    
    def validate_address(self,value):
        if not re.match(r'^[A-Za-z0-9\s,\.]+$',value):
            raise serializers.ValidationError("Address must not conatin special character other than dot(>) and comma(,).")
        return value
    
    def validate_place(self,value):
        if not value.isalpha():
            raise serializers.ValidationError("Place must conatin only alphabets.")
        return value
    
    def validate_phone(self,value):
        if not value.isdigit() or len(value) !=10:
            raise serializers.ValidationError("Phone number must be 10 digits.")
        if Shop.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A shop with this phone number already exists.")
        return value

    def validate_password(self,value):
        if len(value) < 8 or len(value) > 17:
            raise serializers.ValidationError("The password should be min 8 to max 17 character.")   
        return value     
    
    def validate(self,data):
        if data['password']!=data['re_enter_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self,validated_data):
        user_data = {
            'username':validated_data['username'],
            'email':validated_data['email'],
            'password':validated_data['password'],
        }
        user=CustomUser.objects.create_user(**user_data)
        user.is_active = True
        user.is_shop = True
        user.save()
        shop_data ={
            'user': user,
            'shop_name':validated_data['shop_name'],
            'shop_license_number' :validated_data['shop_license_number'],
            'address' :validated_data['address'],
            'place' :validated_data['place'],
            'phone' :validated_data['phone'],
            'is_verified' :False,
        }
        Shop.objects.create(**shop_data)
        return user
    