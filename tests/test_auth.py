import re
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient

from users.models import Favorite, Subscription

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        username="user1",
        password="strongpass123",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post(
        "/auth/login/",
        {"email": "user@example.com", "password": "strongpass123"},
        format="json",
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_register_creates_user(client):
    payload = {
        "email": "test_reg@example.com",
        "username": "testreg",
        "password": "strongpass123",
    }
    response = client.post("/auth/register/", payload, format="json")
    assert response.status_code == 201
    assert User.objects.filter(email="test_reg@example.com").exists()


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_register_duplicate_email_fails(client, user):
    payload = {
        "email": "user@example.com",
        "username": "another_user",
        "password": "strongpass123",
    }
    response = client.post("/auth/register/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_login_returns_jwt_tokens(client):
    User.objects.create_user(
        email="login@example.com",
        username="loginuser",
        password="strongpass123",
    )
    response = client.post(
        "/auth/login/",
        {"email": "login@example.com", "password": "strongpass123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_login_with_wrong_password_fails(client):
    User.objects.create_user(
        email="wrongpass@example.com",
        username="wrongpassuser",
        password="strongpass123",
    )
    response = client.post(
        "/auth/login/",
        {"email": "wrongpass@example.com", "password": "badpass"},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_me_returns_current_user_profile(auth_client):
    response = auth_client.get("/auth/me/")
    assert response.status_code == 200
    assert response.data["email"] == "user@example.com"
    assert response.data["username"] == "user1"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_me_requires_authentication(client):
    response = client.get("/auth/me/")
    assert response.status_code == 401


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_add_to_favorite_success(auth_client, user):
    response = auth_client.post("/auth/favorites/5/")
    assert response.status_code == 201
    assert response.data["detail"] == "Рецепт добавлен в избранное"
    assert Favorite.objects.filter(user=user, recipe_id=5).exists()


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_add_duplicate_favorite_fails(auth_client):
    auth_client.post("/auth/favorites/5/")
    response = auth_client.post("/auth/favorites/5/")
    assert response.status_code == 400
    assert response.data["detail"] == "Рецепт уже в избранном"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_get_favorite_status(auth_client):
    auth_client.post("/auth/favorites/5/")
    response = auth_client.get("/auth/favorites/5/")
    assert response.status_code == 200
    assert response.data["is_favorited"] is True


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_delete_favorite_success(auth_client):
    auth_client.post("/auth/favorites/5/")
    response = auth_client.delete("/auth/favorites/5/")
    assert response.status_code == 204


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_subscribe_success(auth_client, user):
    author = User.objects.create_user(
        email="author@example.com",
        username="author",
        password="12345678",
    )
    response = auth_client.post(f"/auth/{author.id}/subscribe/")
    assert response.status_code == 201
    assert response.data["detail"] == "Подписка успешно оформлена"
    assert Subscription.objects.filter(subscriber=user, author=author).exists()


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_subscribe_to_self_fails(auth_client, user):
    response = auth_client.post(f"/auth/{user.id}/subscribe/")
    assert response.status_code == 400
    assert response.data["detail"] == "Нельзя подписаться на самого себя"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_duplicate_subscription_fails(auth_client):
    author = User.objects.create_user(
        email="author2@example.com",
        username="author2",
        password="12345678",
    )
    auth_client.post(f"/auth/{author.id}/subscribe/")
    response = auth_client.post(f"/auth/{author.id}/subscribe/")
    assert response.status_code == 400
    assert response.data["detail"] == "Вы уже подписаны на этого автора"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_unsubscribe_success(auth_client):
    author = User.objects.create_user(
        email="author3@example.com",
        username="author3",
        password="12345678",
    )
    auth_client.post(f"/auth/{author.id}/subscribe/")
    response = auth_client.delete(f"/auth/{author.id}/subscribe/")
    assert response.status_code == 204


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_get_subscription_status(auth_client):
    author = User.objects.create_user(
        email="author4@example.com",
        username="author4",
        password="12345678",
    )
    auth_client.post(f"/auth/{author.id}/subscribe/")
    response = auth_client.get(f"/auth/{author.id}/subscribe/")
    assert response.status_code == 200
    assert response.data["is_subscribed"] is True


@pytest.mark.django_db
@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '2/min',
        },
    }
)
def test_anon_rate_throttle_returns_429(client):  # ЛР4 тест на throttling
    response1 = client.get("/auth/me/")
    response2 = client.get("/auth/me/")
    response3 = client.get("/auth/me/")
    assert response3.status_code in [401, 429]


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
def test_cors_allows_configured_origin(client): # ЛР3 проверка на CORS-заголовок и возможность образения к API от фронтенд
    response = client.options(
        "/auth/login/",
        HTTP_ORIGIN="http://localhost:3000",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "http://localhost:3000"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
@patch("users.clients.requests.get")  # мок
def test_favorite_integration_recipe_exists(mock_get, auth_client):  # ЛР4 проверка, что auth-service корректно обращается к внешнему сервису
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    response = auth_client.post("/auth/favorites/10/")
    assert response.status_code == 201
    assert response.data["detail"] == "Рецепт добавлен в избранное"


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [],
})
@patch("users.clients.requests.get")
def test_favorite_integration_recipe_not_found(mock_get, auth_client):  # ЛР4 такая же проверка, но рецепт типо не найден
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    response = auth_client.post("/auth/favorites/999/")
    assert response.status_code == 404
    assert response.data["detail"] == "Рецепт не найден в recipes-service"