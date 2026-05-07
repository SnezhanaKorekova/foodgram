from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

# --- НОВЫЕ МОДЕЛИ (2 этап) ---

class Subscription(models.Model):
    subscriber = models.ForeignKey(  # кто подписывается
        User, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(  # на кого
        User, 
        on_delete=models.CASCADE, 
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        # Нельзя подписаться на одного автора дважды (на уровне БД)
        unique_together = ('subscriber', 'author')

class Favorite(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    # recipe_id хранится просто как число, потому что сама модель 
    # рецепта лежит в базе данных микросервиса Люды (recipes-service)
    recipe_id = models.IntegerField(verbose_name='ID Рецепта')

    class Meta:
        # Нельзя добавить один рецепт в избранное дважды
        unique_together = ('user', 'recipe_id')