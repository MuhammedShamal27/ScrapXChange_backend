from django.urls import path
from . views import *

urlpatterns = [
    path('login/',AdminLoginView.as_view(),name='admin_login'),
    path('admin_home/',AdminHomeView.as_view(),name='admin_home'),
    path('user-list/',UserListView.as_view(),name='admin_user_list'),
    path('user-list/<int:id>/',UserDetailsView.as_view(),name='admin_user_details'),
    path('user-list/<int:id>/block-unblock/',UserBlockView.as_view(),name='admin_block-unblock_user'),
    path('shop-list/',ShopListView.as_view(),name='admin_shop_list'),
    path('shop-details/<int:id>/',ShopDetailsView.as_view(),name='admin_shop_detials'),
    path('shop-details/<int:id>/<str:action>/',ShopBlockView.as_view(),name='admin_block_shop'),
    path('shop-request-list/',ShopRequestListView.as_view(),name='admin_shop_request_list'),
    path('shop-request-list/<int:id>/',ShopRequestDetailView.as_view(),name='admin_shop_request_details'),
    path('shop-request-list/<int:id>/accept/',AcceptShopView.as_view(),name='admin_accept_shop'),
    path('shop-request-list/<int:id>/reject/',RejectShopView.as_view(),name='admin_reject_shop'),
]
