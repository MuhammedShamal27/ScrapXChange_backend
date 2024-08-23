from django.urls import path
from .views import *


urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='user_register'),
    path('verify-otp/',OTPVerificationView.as_view(),name='verify_otp'),
    path('resend-otp/',ResendOTPView.as_view(),name='resend_otp'),
    path('password-reset-request/',PasswordResetRequestView.as_view(),name='password-reset-request'),
    path('password-otp/',EmailOTPVerificationView.as_view(),name='password-otp'),
    path('password-reset/',PasswordResetView.as_view(),name='password-reset'),
    path('login/',UserLoginView.as_view(),name='user_login'),
    path('',HomePageView.as_view(),name='user_home'),
    path('profile/',UserProfileView.as_view(),name='user_profile'),
    path('edit-profile/',EditUserProfileView.as_view(),name='edit_user_profile'),
    path('shops/',ShopListView.as_view(),name='shop-list'),
    path('shops/<int:shop_id>/products/', ShopProductListView.as_view(), name='shop-products'),
    path('scrap-collection-request/',CollectionRequestCreateView.as_view(),name='scrap-colection-request')
]
