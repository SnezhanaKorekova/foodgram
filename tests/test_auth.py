import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from users.models import Favorite, Subscription

User = get_user_model()


@pytest.mark.django_db
def test_register_creates_user():
    client = APIClient()
    payload = {
        "email": "test_reg@example.com",
        "username": "testreg",
        "password": "strongpass123",
    }
    response = client.post("/auth/register/", payload, format="json")
    assert response.status_code == 201
    assert User.objects.filter(email="test_reg@example.com").exists()


@pytest.mark.django_db
def test_login_returns_jwt_tokens():
    user = User.objects.create_user(
        email="login@example.com",
        username="loginuser",
        password="strongpass123",
    )
    client = APIClient()
    response = client.post(
        "/auth/login/",
        {"email": "login@example.com", "password": "strongpass123"},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_me_returns_current_user_profile():
    user = User.objects.create_user(
        email="me@example.com",
        username="meuser",
        password="strongpass123",
    )
    client = APIClient()
    login_resp = client.post(
        "/auth/login/",
        {"email": "me@example.com", "password": "strongpass123"},
        format="json",
    )
    token = login_resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = client.get("/auth/me/")
    assert resp.status_code == 200
    assert resp.data["email"] == "me@example.com"
    assert resp.data["username"] == "meuser"


# новые тесты (2 этап)


@pytest.fixture
def auth_client():
    # Фикстура для создания клиента с JWT токеном
    client = APIClient()
    user = User.objects.create_user(
        email="test2@example.com",
        username="test2",
        password="123"
    )
    # Получаем токен
    response = client.post("/auth/login/", {"email": "test2@example.com", "password": "123"})
    token = response.data["access"]
    # Прописываем токен в заголовки клиента
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client, user


@pytest.mark.django_db
def test_add_to_favorite(auth_client):
    # Тест: добавление рецепта в избранное
    client, user = auth_client

    # Пытаемся добавить рецепт с ID 5
    response = client.post("/auth/favorites/5/")

    assert response.status_code == 201
    assert response.data["detail"] == "Рецепт добавлен в избранное"
    assert Favorite.objects.filter(user=user, recipe_id=5).exists()


@pytest.mark.django_db
def test_subscribe_to_user(auth_client):
    # Тест: подписка на другого пользователя
    client, subscriber = auth_client

    # Создаем автора, на которого будем подписываться
    author = User.objects.create_user(
        email="author@example.com",
        username="author",
        password="123"
    )

    response = client.post(f"/auth/{author.id}/subscribe/")

    assert response.status_code == 201
    assert response.data["detail"] == "Подписка успешно оформлена"
    assert Subscription.objects.filter(subscriber=subscriber, author=author).exists()