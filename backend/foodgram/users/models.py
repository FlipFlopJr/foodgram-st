from django.contrib.auth.models import AbstractUser
from django.db import models


class UserModel(AbstractUser):
    """Модель пользователя"""

    first_name = models.CharField("name", max_length=150)
    surname = models.CharField("surname", max_length=150)
    avatar = models.ImageField(
        "avatar", upload_to="avatars/", blank=True, null=True
    )
    email = models.EmailField("email", unique=True, max_length=254)

    REQUIRED_FIELDS = ["username", "first_name", "surname"]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return str(self.email)


class SubscriptionModel(models.Model):
    """Модель подписки"""

    user_to = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="followers"
    )

    user_from = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        ordering = ["user_from"]
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"
        constraints = [
            models.UniqueConstraint(
                fields=["user_from", "user_to"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
