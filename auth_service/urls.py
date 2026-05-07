from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger/OpenAPI документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Auth endpoints
    path('auth/', include('users.urls')),  # кастомные эндпоинты
    path('auth/', include('djoser.urls')),  # djoser users/*
    path('auth/', include('djoser.urls.jwt')),  # djoser jwt/*
]