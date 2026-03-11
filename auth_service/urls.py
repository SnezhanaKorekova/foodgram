from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),      # наши кастомные эндпоинты
    path('auth/', include('djoser.urls')),     # djoser users/*
    path('auth/', include('djoser.urls.jwt')), # djoser jwt/*
]
