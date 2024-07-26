from django.urls import path
from .views import *


urlpatterns = [
    path('user/register/',UserRegisterView.as_view(),name='user_register'),
    path('user/verify-otp/',OTPVerificationView.as_view(),name='verify-otp'),
]
