from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('me/', views.MeView.as_view(), name='me'),

    # Эндпоинты (2 этап)
    path('<int:id>/subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('favorites/<int:id>/', views.FavoriteView.as_view(), name='favorite'),
]