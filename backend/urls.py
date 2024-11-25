from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView
)

    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/',include('user.urls')),
    path('api/shop/',include('shop.urls')),
    path('api/scrapxchange_admin/',include('scrapxchange_admin.urls')),
    path('token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),

]
