import requests
import logging

logger = logging.getLogger(__name__)

# Ссылка на сервис Люды внутри Docker-сети
# В будущем, когда соберём общий docker-compose, это имя будет актуальным
RECIPES_SERVICE_URL = "http://recipes-service:8000/api/recipes/"

def check_recipe_exists(recipe_id: int) -> bool:
    # HTTP-запрос к микросервису recipes-service для проверки существования рецепта.

    try:
        # Пытаемся обратиться в сервис Люды
        response = requests.get(f"{RECIPES_SERVICE_URL}{recipe_id}/", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # мок: пока общего докера нет, или сервис Люды выключен,
        # мы просто разрешаем добавление любого recipe_id > 0 для теста
        logger.warning(f"recipes-service недоступен. Используем Mock для recipe_id={recipe_id}")
        return int(recipe_id) > 0