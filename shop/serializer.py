from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from user.models import *
from datetime import *
from . models import *
import re
from scrapxchange_admin.models import *

# -------- Shop Registration -------
# ----------------------------------
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


 
class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = '__all__'
    
class ShopLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password']

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        try:
            user = CustomUser.objects.get(email=email)
            shop = Shop.objects.get(user=user)
            
            if shop.is_blocked:
                raise serializers.ValidationError("This shop is blocked.")
            if not shop.is_verified:
                raise serializers.ValidationError("The shop is not yet verified by the Admin.")
            if shop.is_rejected:
                raise serializers.ValidationError("This shop has been rejected by the Admin.")
            
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Shop with this email does not exist.")
        except Shop.DoesNotExist:
            raise serializers.ValidationError("Shop information is not available.")
        
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Incorrect Password.")
        
        refresh = RefreshToken.for_user(user)

        return {
            'email': user.email,
            'username': user.username,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }


               
class ShopHomeSerializer(serializers.ModelSerializer):
    user_profile = serializers.ImageField(source='shop.profile_picture',read_only=True)

    class Meta:
        model = CustomUser
        fields = ['username','user_profile']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self,value):
        if not value.isalpha():
            raise serializers.ValidationError("Category name should only contain alphabets.")
        return value
        
class CategoryCreateSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Category
        fields = ['name', 'image', 'description']
        
    def validate_name(self, value):
        user = self.context['request'].user
        print('User in serializer:', user)
        if Category.objects.filter(user=user, name__iexact=value).exists():
            print('Category with this name already exists.')
            raise serializers.ValidationError("A category with this name already exists in your shop.")
        if not value.isalpha():
            raise serializers.ValidationError("Category name should only contain alphabets.")
        return value
    
    def validate_image(self, value):
        if not value or not hasattr(value, 'content_type'):
            raise serializers.ValidationError("Please upload a valid image.")
        if not value.content_type.startswith('image'):
            raise serializers.ValidationError("File must be an image.")
        return value

    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        if len(value) < 10:
            raise serializers.ValidationError("Description should be at least 10 characters long.")
        return value

    def validate(self, data):
        print('Data in validate method:', data)
        if not data.get('name') or not data.get('image') or not data.get('description'):
            raise serializers.ValidationError("All fields (name, image, and description) must be filled.")
        user = self.context['request'].user
        shop = Shop.objects.get(user=user)
        if not shop.is_verified or not user.is_shop:
            raise serializers.ValidationError("Only verified shops can create categories.")
        return data

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
        
class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'image', 'description']
        
    

    def validate_name(self, value):
        user = self.context['request'].user
        print('serializer',user)
        category_id = self.instance.id if self.instance else None
        if Category.objects.filter(user=user,name__iexact=value ).exclude(id=category_id).exists():
            raise serializers.ValidationError("A category with this name already exists with this shop.")
        if not value.isalpha():
            raise serializers.ValidationError("Category name should only contain alphabets.")
        return value

    def validate_image(self, value):
        if value and not hasattr(value, 'content_type'):
            raise serializers.ValidationError("Please upload a valid image.")
        if value and not value.content_type.startswith('image'):
            raise serializers.ValidationError("File must be an image.")
        return value

    def validate_description(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Description should be at least 10 characters long.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise serializers.ValidationError("Shop associated with this user does not exist.")
        
        if not shop.is_verified or not user.is_shop:
            raise serializers.ValidationError("Only verified shops can edit categories.")
        return data
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)  
        instance.save()
        return instance

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category_name', 'image', 'user']


class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'image']

    def validate_name(self, value):
        user = self.context['request'].user
        if not value.isalpha():
            raise serializers.ValidationError("Product name should only contain alphabets.")
        if Product.objects.filter(name=value, user=user).exists():
            raise serializers.ValidationError("A product with this name already exists.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Product price must be greater than zero.")
        return value

    def validate_category(self, value):
        user = self.context['request'].user
        if not Category.objects.filter(id=value.id, user=user).exists():
            raise serializers.ValidationError("Selected category does not exist in your shop or you do not have permission to use it.")
        return value

    def validate_image(self, value):
        if value and not hasattr(value, 'content_type'):
            raise serializers.ValidationError("Please upload a valid image.")
        if value and not value.content_type.startswith('image'):
            raise serializers.ValidationError("File must be an image.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise serializers.ValidationError("Shop associated with this user does not exist.")
    
        if not shop.is_verified:
            raise serializers.ValidationError("Only verified shops can create products.")
        
        data['user'] = user
        return data
    

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'image']

    def validate_name(self, value):
        user = self.context['request'].user
        if not value.isalpha():
            raise serializers.ValidationError("Product name should only contain alphabets.")
        product_id = self.instance.id if self.instance else None
        if Product.objects.filter(name=value, user=user).exclude(id=product_id).exists():
            raise serializers.ValidationError("A product with this name already exists in your shop.")
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Product price must be greater than zero.")
        return value

    def validate_category(self, value):
        user = self.context['request'].user
        if not Category.objects.filter(id=value.id, user=user).exists():
            raise serializers.ValidationError("Selected category does not exist in your shop or you do not have permission to use it.")
        return value
    
    def validate_image(self, value):
        if value and not hasattr(value, 'content_type'):
            raise serializers.ValidationError("Please upload a valid image.")
        if value and not value.content_type.startswith('image'):
            raise serializers.ValidationError("File must be an image.")
        return value
    
    def validate(self, data):
        user = self.context['request'].user

        try:
            shop = Shop.objects.get(user=user)
        except Shop.DoesNotExist:
            raise serializers.ValidationError("Shop associated with this user does not exist.")
        
        if not shop.is_verified:
            raise serializers.ValidationError("Only verified shops can update products.")
        return data
    


class ProductDetailsSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
        
class ScrapRequestListSerializer(serializers.ModelSerializer):
    
    products=ProductDetailsSerilaizer(many=True)
    
    class Meta:
        model = CollectionRequest
        fields = "__all__"
    
        
class SheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = [] 

    def validate(self, data):
        instance = self.instance
        shop = self.context['request'].user.shop
        
        if instance.date_requested < date.today():
            raise serializers.ValidationError("The requested date is in the past. Please reschedule to a coming date.")
        
        if CollectionRequest.objects.filter(scheduled_date=instance.date_requested, shop=shop, is_scheduled=True).count() >= 5:
            raise serializers.ValidationError("There are no more slots for the requested date. Please reschedule.")

        return data
    
class RescheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['scheduled_date']

    def validate_scheduled_date(self, value):
        shop = self.context['request'].user.shop
        today = date.today()
        one_week_from_today = today + timedelta(weeks=1)
        
        print('the value',value)
        if value < today:
            raise serializers.ValidationError("The selected date is in the past. Please choose a date from today or in the coming date.")
        
        if value > one_week_from_today:
            raise serializers.ValidationError("The selected date cannot be more than a week from today. Please choose a date within the next week.")
        
        if CollectionRequest.objects.filter(scheduled_date=value, shop=shop, is_scheduled=True).count() >= 5:
            raise serializers.ValidationError("There are no more slots for the requested date. Please reschedule.")
        return value


    
class TodaySheduledSerializer(serializers.ModelSerializer):
    
    products = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = CollectionRequest
        fields = "__all__"
        
        

class TransactionProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = TransactionProduct
        fields = ['product_id', 'quantity']

class ScrapCollectionSerializer(serializers.ModelSerializer):
    transaction_products = TransactionProductSerializer(many=True, write_only=True)
    collection_request_id = serializers.IntegerField()

    class Meta:
        model = Transaction
        fields = ['id', 'collection_request_id', 'transaction_products', 'total_quantity', 'total_price']

    def create(self, validated_data):
        collection_request_id = validated_data.get('collection_request_id')
        transaction_products_data = validated_data.pop('transaction_products')

        collection_request = CollectionRequest.objects.get(id=collection_request_id)
        total_quantity = 0
        total_price = 0
        
        transaction = Transaction.objects.create(
            collection_request=collection_request,
            date_picked=date.today(),
        )

        for product_data in transaction_products_data:
            product = Product.objects.get(id=product_data['product_id'])
            quantity = int(product_data['quantity'])
            total_quantity += quantity
            total_price += quantity * product.price

            TransactionProduct.objects.create(
                transaction=transaction,
                product=product,
                quantity=quantity
            )

        transaction.total_quantity = total_quantity
        transaction.total_price = total_price
        transaction.save()

        return transaction
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category']

class TransactionProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = TransactionProduct
        fields = ['product', 'quantity']

class ConfirmCollectionSerializer(serializers.ModelSerializer):
    transaction_products = TransactionProductSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['id', 'total_quantity', 'total_price', 'date_picked',  'transaction_products']
        
class CollectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['id','is_collected']

class PaymentSuccessfullSerializer(serializers.ModelSerializer):
    
    collection_request = CollectionRequestSerializer()
    
    class Meta:
        model = Transaction
        fields=['id','payment_method','payment_id','razorpay_order_id','collection_request']
        
class TransactionSerializer(serializers.ModelSerializer):
    transaction_products = TransactionProductSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['total_quantity', 'total_price', 'date_picked', 'payment_method', 'transaction_products']

    
class InvoiceSerializer(serializers.ModelSerializer):
    shop = ShopSerializer()
    transactions = TransactionSerializer(many=True)

    class Meta:
        model = CollectionRequest
        fields = [
            'id', 'user', 'shop', 'date_requested', 'scheduled_date', 
            'name', 'address', 'landmark', 'pincode', 'phone', 'upi',
            'add_note', 'reject_message', 'is_accepted', 'is_rejected', 
            'is_scheduled', 'is_collected', 'transactions'
        ]

# ---------------------------------------------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        
class CustomUserSerializer(serializers.ModelSerializer):
    User_profile=UserProfileSerializer()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username','User_profile']
        


        
        
class ShopFetchLastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'timestamp', 'message']
        
        
class ShopChatRoomSerializer(serializers.ModelSerializer):
    # messages = serializers.SerializerMethodField()
    user = CustomUserSerializer()
    shop = ShopSerializer()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'user', 'shop', 'created_at']
        
    # def get_messages(self, obj):
    #     messages = Message.objects.filter(room=obj)
    #     return ShopFetchLastMessageSerializer(messages, many=True).data
        
    def create(self, validated_data):
        print('the validated data',validated_data)
        room, created = ChatRoom.objects.get_or_create(
            user=validated_data['user'],
            shop=validated_data['shop'],
        )
        return room
    
    
class ShopMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    audio = serializers.ImageField(required=False)
    image = serializers.ImageField(required=False)
    video = serializers.ImageField(required=False)
     
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'receiver', 'timestamp', 'message','audio','image','video','sender_username', 'receiver_username']
        
    def validate_image(self, value):
        if value and not value.name.endswith(('jpg', 'jpeg', 'png', 'gif')):
            raise serializers.ValidationError('Unsupported image file type.')
        return value

    def validate_video(self, value):
        if value and not value.name.endswith(('mp4', 'avi', 'mov')):
            raise serializers.ValidationError('Unsupported video file type.')
        return value

    def validate_audio(self, value):
        if value and not value.name.endswith(('webm', 'mp3', 'wav', 'ogg')):
            raise serializers.ValidationError('Unsupported audio file type.')
        return value
    
    def create(self, validated_data):
        
        print('the validated data',validated_data)
        room = validated_data['room']
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        
        if sender != room.user and sender != room.shop.user:
            raise serializers.ValidationError("Sender is not part of this chat room.")
        
        if receiver != room.user and receiver != room.shop.user:
            raise serializers.ValidationError("Receiver is not part of this chat room.")
        
        return super().create(validated_data)
    
    
class ShopProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username',read_only=True)
    email = serializers.EmailField(source ='user.email',read_only=True)

    class Meta:
        model = Shop
        fields =  ['username', 'email', 'shop_name', 'shop_license_number', 'phone', 'address', 'place', 'profile_picture','latitude','longitude']
        
        
class ShopReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['receiver', 'reason']

    def create(self, validated_data):
        # Set the sender to the currently authenticated user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
    
    
class ShopProfileAndLocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Shop
        fields = ['profile_picture', 'latitude', 'longitude']  
    def update(self, instance, validated_data):
        # Update only the fields we are interested in
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance
    
    
    


class CollectionRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['name', 'address', 'pincode', 'phone', 'date_requested', 'scheduled_date','is_accepted','is_rejected','is_scheduled']


class TransactionsSerializer(serializers.ModelSerializer):
    collection_request = CollectionRequestsSerializer()
    transaction_products = TransactionProductSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['id', 'collection_request', 'total_quantity', 'total_price', 'date_picked', 'payment_method', 'transaction_products']     
        

class UserWithCompletedTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username']

class ShopDashboardSerializer(serializers.Serializer):
    pending_collections = CollectionRequestsSerializer(many=True)
    today_pending_collections = CollectionRequestsSerializer(many=True)
    completed_transaction_users = UserWithCompletedTransactionsSerializer(many=True)
    pending_requests = CollectionRequestsSerializer(many=True)
    transactions = TransactionsSerializer(many=True)
    total_collected = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
class ShopNotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()  # to display sender's username
    receiver = serializers.StringRelatedField()  # to display receiver's username
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'message', 'is_read', 'created_at']