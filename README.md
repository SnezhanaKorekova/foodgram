# Foodgram Auth Service

Микросервис авторизации и пользовательских действий для проекта **Foodgram**.  
Стек: **Django + Django REST Framework + JWT + PostgreSQL + Docker**.

## Основные эндпоинты

| Метод | URL | Описание |
|------|-----|----------|
| POST | `/auth/register/` | Регистрация пользователя (`email`, `username`, `password`) |
| POST | `/auth/login/` | Логин и получение JWT токенов (`access`, `refresh`) |
| GET | `/auth/me/` | Профиль текущего авторизованного пользователя |
| POST | `/auth/favorites/{id}/` | Добавить рецепт в избранное |
| GET | `/auth/favorites/{id}/` | Проверить, находится ли рецепт в избранном |
| DELETE | `/auth/favorites/{id}/` | Удалить рецепт из избранного |
| POST | `/auth/{id}/subscribe/` | Подписаться на автора |
| GET | `/auth/{id}/subscribe/` | Проверить статус подписки |
| DELETE | `/auth/{id}/subscribe/` | Отписаться от автора |

## Этап 1

На первом этапе были реализованы:

- Django-проект и базовая структура микросервиса;
- кастомная модель `User` на основе `AbstractUser`;
- регистрация пользователя через `POST /auth/register/`;
- логин через `POST /auth/login/` с выдачей JWT токенов;
- получение профиля текущего пользователя через `GET /auth/me/`;
- базовые unit-тесты на регистрацию, логин и профиль;
- контейнеризация через `Dockerfile` и `docker-compose.yml`;
- запуск PostgreSQL и auth-service в Docker.

## Этап 2

На втором этапе были добавлены пользовательские действия:

- модель `Favorite` (`user`, `recipe_id`) для хранения избранных рецептов;
- модель `Subscription` (`subscriber`, `author`) для подписок на авторов;
- эндпоинты для избранного:
  - `POST /auth/favorites/{id}/`
  - `GET /auth/favorites/{id}/`
  - `DELETE /auth/favorites/{id}/`
- эндпоинты для подписок:
  - `POST /auth/{id}/subscribe/`
  - `GET /auth/{id}/subscribe/`
  - `DELETE /auth/{id}/subscribe/`
- HTTP-клиент для связи с `recipes-service`;
- проверка существования рецепта через межсервисный HTTP-запрос;
- дополнительные unit-тесты;
- ограничение доступа через `IsAuthenticated` для защищённых эндпоинтов.

## Этап 3

На третьем этапе сервис был подготовлен к интеграции в общую микросервисную систему:

- **Rate limiting** через Django REST Framework throttling:
  - `UserRateThrottle`
  - `AnonRateThrottle`
- **CORS** для фронтенда:
  - подключён `django-cors-headers`
  - разрешены локальные origin для frontend development
- **Swagger / OpenAPI документация**:
  - подключён `drf-spectacular`
  - Swagger UI: `/api/docs/`
  - OpenAPI schema: `/api/schema/`
- **Расширенное тестовое покрытие**:
  - итог: **19 passing tests**
  - тесты на регистрацию, логин, профиль, избранное, подписки
  - тесты на CORS, throttling и интеграцию с `recipes-service`
- **Nginx gateway**:
  - подготовлен reverse proxy конфиг для единой точки входа в систему
- **Общий docker-compose шаблон**:
  - подготовлен `docker-compose.stage3.yml` для будущего объединения микросервисов

## Локальный запуск

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

## Запуск через Docker

```bash
docker-compose up --build
```

Сервис будет доступен по адресу:

```text
http://127.0.0.1:8001/
```

## Swagger / OpenAPI

После запуска сервиса документация доступна по адресам:

- Swagger UI: `http://127.0.0.1:8001/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8001/api/schema/`

## Тесты

Запуск тестов внутри Docker-контейнера:

```bash
docker-compose exec auth-service pytest -v
```

Текущее покрытие: **19 passing tests**.

## Инфраструктура этапа 3

Для интеграции в общий проект подготовлены:

- `infra/nginx/nginx.conf` — конфигурация Nginx gateway;
- `docker-compose.stage3.yml` — шаблон общего docker-compose для объединения сервисов.