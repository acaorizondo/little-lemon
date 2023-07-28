from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import  obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('LittleLemonAPI.urls')),
    
    #path('auth/', include('djoser.urls')),
    #path('auth/', include('djoser.urls.authtoken')),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    
    path('api-token-auth/', obtain_auth_token),
]
