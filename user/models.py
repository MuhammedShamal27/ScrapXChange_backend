from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

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
    password=models.CharField(max_length=33)
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
    is_blocked= models.BooleanField(default=False)
    otp = models.CharField(max_length=6,blank=True,null=True)


    def __str__(self):
        return self.user.email