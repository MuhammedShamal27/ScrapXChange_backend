from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from shop.models import *

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self,email,username,password=None):
        if not email:
            raise ValueError('The Email Field Must Be Set')
        email=self.normalize_email(email)
        user=self.model(email=email,username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,username,password=None):
        user=self.create_user(email=self.normalize_email(email),
                                username=username,
                                password=password,)
        user.is_active=True
        user.is_superuser=True
        user.is_staff=True
        
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=33,blank=True)
    password=models.CharField(max_length=200)
    is_active=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_shop=models.BooleanField(default=False)
    date_joined=models.DateField(auto_now_add=True)
    last_login=models.DateField(auto_now=True)


    objects=CustomUserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username
    
    def has_perm(self,perm,obj=None):
        return self.is_superuser
    
    def has_module_perms(self,add_label):
        return True
    

class UserProfile(models.Model):
    user =models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name='User_profile')
    address=models.CharField(max_length=255,blank=True)
    pincode=models.CharField(max_length=10,blank=True)
    phone=models.CharField(max_length=15,blank=True)
    alternative_phone=models.CharField(max_length=15,blank=True)
    profile_picture =models.ImageField(upload_to='Profile_pics',blank=True)
    warning_count = models.IntegerField(default=0)
    is_blocked= models.BooleanField(default=False)
    otp = models.CharField(max_length=6,blank=True,null=True)
    otp_generated_at = models.DateTimeField(blank=True, null=True)
    is_validated = models.BooleanField(default=False)


    def __str__(self):
        return self.user.email
    
    
class CollectionRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collection_requests')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE,  related_name='collection_requests')
    date_requested = models.DateField()
    scheduled_date=models.DateField(null=True , blank=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    upi = models.CharField(max_length=50)
    products = models.ManyToManyField(Product, related_name='collection_requests')  
    add_note=models.TextField()
    reject_message = models.CharField(max_length=100 , blank=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_scheduled = models.BooleanField(default=False)
    is_collected = models.BooleanField(default=False)

    def __str__(self):
        shop_name = self.shop.shop_name if self.shop else "Deleted Shop"
        return f"Request by {self.user.email} to {shop_name}"

    
class TransactionProduct(models.Model):
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='transaction_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Transaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
    ]
    collection_request = models.ForeignKey(CollectionRequest, on_delete=models.CASCADE, related_name='transactions')
    products = models.ManyToManyField(Product, through=TransactionProduct)
    total_quantity = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    date_picked = models.DateField()
    payment_method = models.CharField(max_length=100 , choices=PAYMENT_METHOD_CHOICES)
    payment_id=models.CharField(max_length=100,null=True,blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Transaction for {self.collection_request.user.email} at {self.collection_request.shop.shop_name}"


class ChatRoom(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_rooms')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.id} - {self.user.username} and {self.shop.shop_name}"  # Using the primary key as room_id


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    video = models.FileField(upload_to='messages/videos/', blank=True, null=True)
    audio = models.FileField(upload_to='messages/audio/', blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('general', 'General'),
        ('report', 'Report'),
    ]
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    
    def __str__(self):
        return f"Notification from {self.sender} to {self.receiver}"
    
