from django.db import models
from django.conf import settings
from user.models import *

# Create your models here.

class Shop(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='shop')
    shop_name = models.CharField(max_length=33)
    shop_license_number = models.CharField(max_length=50,unique=True)
    phone = models.CharField(max_length=15,unique=True)
    address = models.TextField()
    place=models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='shop_pics',blank=True)
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name
    
class Category(models.Model):
    name = models.CharField(max_length=33)
    image = models.ImageField(upload_to='category_pics',blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='categories')
    

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10 ,decimal_places=2)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    image = models.ImageField(upload_to='product_pics',blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='products')
    

    def __str__(self):
        return self.name
    


    
    
    
    
    
    