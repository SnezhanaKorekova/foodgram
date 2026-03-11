import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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
