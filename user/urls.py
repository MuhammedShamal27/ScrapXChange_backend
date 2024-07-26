from django.urls import path
from .views import *


urlpatterns = [
    path('user/register/',UserRegisterView.as_view(),name='user_register'),
    path('user/verify-otp/',OTPVerificationView.as_view(),name='verify_otp'),
    path('user/resend-otp/',ResendOTPView.as_view(),name='resend_otp'),
    path('user/password-reset-request/',PasswordRestRequestView.as_view(),name='password-reset-request'),
    path('user/password-reset/',PasswordResetView.as_view(),name='password-reset'),
    path('user/login/',UserLoginView.as_view(),name='user_login'),
    path('user/profile/',UserProfileView.as_view(),name='user_profile'),
]
