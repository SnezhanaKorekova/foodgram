# Foodgram Auth Service (Этап 1)

**Микросервис авторизации** для проекта Foodgram.  
Django + DRF + JWT + PostgreSQL + Docker.

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/auth/register/` | Регистрация (email, username, password) |
| `POST` | `/auth/login/` | Логин → JWT токены (access, refresh) |
| `GET` | `/auth/me/` | Профиль текущего пользователя |

## Локальный запуск

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
