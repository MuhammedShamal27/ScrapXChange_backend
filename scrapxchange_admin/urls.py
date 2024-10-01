from django.urls import path
from . views import *

urlpatterns = [
    path('login/',AdminLoginView.as_view(),name='admin_login'),
    path('admin_home/',AdminHomeView.as_view(),name='admin_home'),
    path('user-list/',UserListView.as_view(),name='admin_user_list'),
    path('user-list/blocked-user',BlockedUserListView.as_view(),name='admin_user_list'),
    path('user-list/unblocked-user',UnblockedUserListView.as_view(),name='admin_user_list'),
    path('user-details/<int:id>/',UserDetailsView.as_view(),name='admin_user_details'),
    path('user-list/<int:id>/block-unblock/',UserBlockView.as_view(),name='admin_block-unblock_user'),
    path('shop-list/',ShopListView.as_view(),name='admin_shop_list'),
    path('shop-list/blocked-shop',BlockedShopListView.as_view(),name='admin_shop_list'),
    path('shop-list/unblocked-shop',UnblockedShopListView.as_view(),name='admin_shop_list'),
    path('shop-details/<int:id>/',ShopDetailsView.as_view(),name='admin_shop_detials'),
    path('shop-details/<int:id>/block-unblock/',ShopBlockView.as_view(),name='admin_block_shop'),
    path('shop-request-list/',ShopRequestListView.as_view(),name='admin_shop_request_list'),
    path('shop-request-list/<int:id>/',ShopRequestDetailView.as_view(),name='admin_shop_request_details'),
    path('shop-request-list/<int:id>/accept/',AcceptShopView.as_view(),name='admin_accept_shop'),
    path('shop-request-list/<int:id>/reject/',RejectShopView.as_view(),name='admin_reject_shop'),
    path('reports/',ReportView.as_view(),name='report-list'),
    path('report-reason/<int:id>/',ReportReasonsView.as_view(),name='report-reason'),
    path('report-block-unblock/<int:id>/',ReportBlockUnblockView.as_view(),name='report-block-unblock'),
    path('dashboard-data/', DashboardDataView.as_view(), name='dashboard-data'),
]
