from django.urls import path
from . views import *


urlpatterns = [
    path('register/',ShopRegisterView.as_view(),name='shop-register'),
    path('login/',ShopLoginView.as_view(),name='shop-login'),
    path('home/',ShopHomeView.as_view(),name='shop-home'),
    path('category-list/',CategoryListView.as_view(),name='shop-category-list'),
    path('category-creation/',CategoryCreateView.as_view(),name='shop-category-creation'),
    path('category-detail/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'), 
    path('category-update/<int:pk>/',CategoryUpdateView.as_view(),name='category-update'),
    path('product-list/',ProductListView.as_view(),name='shop-product-lsit'),
    path('product-creation/',ProductCreateView.as_view(),name='shop-product-creation'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'), 
    path('product-update/<int:pk>/',ProductUpdateView.as_view(),name='shop-product-update'),
    path('scrap-requests/',ScrapRequestListView.as_view(),name='scrap-requests-list'),
    path('scrap-request-details/<int:pk>/',ScrapRequestDetailsView.as_view(),name='scrap-requests-details'),
    path('schedule-request/<int:pk>/',ScheduleRequestView.as_view(),name='schedule-request'),
    path('reschedule-request/<int:pk>/',RescheduleRequestView.as_view(),name='schedule-request'),
    path('reject-request/<int:pk>/',RejectRequestView.as_view(),name='reject-request'),
    
    
]
