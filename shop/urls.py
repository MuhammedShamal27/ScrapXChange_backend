from django.urls import path
from . views import *


urlpatterns = [
    path('register/',ShopRegisterView.as_view(),name='shop-register'),
    path('login/',ShopLoginView.as_view(),name='shop-login'),
    path('home/',ShopHomeView.as_view(),name='shop-home'),
    path('category-list/',CategoryListView.as_view(),name='shop-category-list'),
    path('category-creation/',CategoryCreateView.as_view(),name='shop-category-creation'),
    path('category-update/<int:pk>/',CategoryUpdateView.as_view(),name='category-update'),
    path('product-list/',ProductListView.as_view(),name='shop-product-lsit'),
    path('product-creation/',ProductCreateView.as_view(),name='shop-product-creation'),
    path('product-update/<int:pk>/',ProductUpdateView.as_view(),name='shop-product-update'),

]
