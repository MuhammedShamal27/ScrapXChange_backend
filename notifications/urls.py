from django.urls import path
from . views import *

urlpatterns = [
    path('save-fcm-token/',SaveFcmToken.as_view(),name="save-fcm-token"),
    path('send-notification-shop/',NotifyShop.as_view(),name="send-notification-for-shop"),
]

