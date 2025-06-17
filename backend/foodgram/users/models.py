from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class UserModel(AbstractUser):
    """Модель пользователя"""

    first_name = models.CharField("name", max_length=150)
    surname = models.CharField("surname", max_length=150)
    avatar = models.ImageField(
        "avatar", upload_to="avatars/", blank=True, null=True
    )
    email = models.EmailField("email", unique=True, max_length=254)
    username = models.CharField("username",
                                max_length=150,
                                unique=True,
                                validators=[
                                    RegexValidator(
                                        regex=(r"^[\w.@+-]+$"),
                                        message=(
                                            "username must contains only letters, "
                                            "digits and signs @/./+/-/_"
                                        ),
                                        code="invalid_username",
                                    )
                                ],
                                )

    REQUIRED_FIELDS = ["username", "first_name", "surname"]
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return self.email


class SubscriptionModel(models.Model):
    """Модель подписки"""

    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="authors",
        verbose_name="Автор",
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписчик",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"
