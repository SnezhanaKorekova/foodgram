from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from djoser.serializers import UserCreateSerializer, UserSerializer

from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Favorite, Subscription
from .clients import check_recipe_exists

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    # по умолчанию SimpleJWT будет использовать email как логин,
    # так как LOGIN_FIELD = 'email' в настройках Djoser


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Только авторизованные

    def post(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.user == author:
            return Response({"detail": "Нельзя подписаться на самого себя"}, status=status.HTTP_400_BAD_REQUEST)

        if Subscription.objects.filter(subscriber=request.user, author=author).exists():
            return Response({"detail": "Вы уже подписаны на этого автора"}, status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(subscriber=request.user, author=author)
        return Response({"detail": "Подписка успешно оформлена"}, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(subscriber=request.user, author=author).first()

        if not subscription:
            return Response({"detail": "Вы не подписаны на этого автора"}, status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, id):
        author = get_object_or_404(User, id=id)
        is_subscribed = Subscription.objects.filter(subscriber=request.user, author=author).exists()
        return Response({"is_subscribed": is_subscribed}, status=status.HTTP_200_OK)


class FavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):  # id - это recipe_id
        # Связь с сервисом Люды
        if not check_recipe_exists(id):
            return Response({"detail": "Рецепт не найден в recipes-service"}, status=status.HTTP_404_NOT_FOUND)

        if Favorite.objects.filter(user=request.user, recipe_id=id).exists():
            return Response({"detail": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=request.user, recipe_id=id)
        return Response({"detail": "Рецепт добавлен в избранное"}, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        favorite = Favorite.objects.filter(user=request.user, recipe_id=id).first()
        if not favorite:
            return Response({"detail": "Этого рецепта нет в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, id):
        is_favorited = Favorite.objects.filter(user=request.user, recipe_id=id).exists()
        return Response({"is_favorited": is_favorited}, status=status.HTTP_200_OK)