from django.urls import path
from . views import *


urlpatterns = [
    path('register/',ShopRegisterView.as_view(),name='shop_register')
]
