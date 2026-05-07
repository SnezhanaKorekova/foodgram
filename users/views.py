from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import User, Favorite, Subscription
from .clients import check_recipe_exists

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """Получение JWT токена (логин по email и password)"""
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """Получение профиля текущего пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        description="Возвращает информацию о текущем авторизованном пользователе"
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SubscribeView(APIView):
    """Управление подписками на авторов"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID автора')],
        responses={
            201: OpenApiResponse(description="Подписка успешно оформлена"),
            400: OpenApiResponse(description="Ошибка валидации (уже подписан или попытка подписаться на себя)"),
        },
        description="Подписаться на автора"
    )
    def post(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.user == author:
            return Response({"detail": "Нельзя подписаться на самого себя"}, status=status.HTTP_400_BAD_REQUEST)

        if Subscription.objects.filter(subscriber=request.user, author=author).exists():
            return Response({"detail": "Вы уже подписаны на этого автора"}, status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(subscriber=request.user, author=author)
        return Response({"detail": "Подписка успешно оформлена"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID автора')],
        responses={
            204: OpenApiResponse(description="Подписка удалена"),
            400: OpenApiResponse(description="Вы не подписаны на этого автора"),
        },
        description="Отписаться от автора"
    )
    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(subscriber=request.user, author=author).first()

        if not subscription:
            return Response({"detail": "Вы не подписаны на этого автора"}, status=status.HTTP_400_BAD_REQUEST)

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID автора')],
        responses={200: {"is_subscribed": "bool"}},
        description="Проверить статус подписки на автора"
    )
    def get(self, request, id):
        author = get_object_or_404(User, id=id)
        is_subscribed = Subscription.objects.filter(subscriber=request.user, author=author).exists()
        return Response({"is_subscribed": is_subscribed}, status=status.HTTP_200_OK)


class FavoriteView(APIView):
    """Управление избранными рецептами"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID рецепта')],
        responses={
            201: OpenApiResponse(description="Рецепт добавлен в избранное"),
            404: OpenApiResponse(description="Рецепт не найден в recipes-service"),
            400: OpenApiResponse(description="Рецепт уже в избранном"),
        },
        description="Добавить рецепт в избранное"
    )
    def post(self, request, id):
        if not check_recipe_exists(id):
            return Response({"detail": "Рецепт не найден в recipes-service"}, status=status.HTTP_404_NOT_FOUND)

        if Favorite.objects.filter(user=request.user, recipe_id=id).exists():
            return Response({"detail": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=request.user, recipe_id=id)
        return Response({"detail": "Рецепт добавлен в избранное"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID рецепта')],
        responses={
            204: OpenApiResponse(description="Рецепт удалён из избранного"),
            400: OpenApiResponse(description="Этого рецепта нет в избранном"),
        },
        description="Удалить рецепт из избранного"
    )
    def delete(self, request, id):
        favorite = Favorite.objects.filter(user=request.user, recipe_id=id).first()
        if not favorite:
            return Response({"detail": "Этого рецепта нет в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[OpenApiParameter(name='id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description='ID рецепта')],
        responses={200: {"is_favorited": "bool"}},
        description="Проверить, добавлен ли рецепт в избранное"
    )
    def get(self, request, id):
        is_favorited = Favorite.objects.filter(user=request.user, recipe_id=id).exists()
        return Response({"is_favorited": is_favorited}, status=status.HTTP_200_OK)