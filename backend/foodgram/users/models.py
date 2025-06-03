from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Foodgram user model"""

    email = models.EmailField("email", unique=True, max_length=254)
    first_name = models.CharField("name", max_length=150)
    last_name = models.CharField("surname", max_length=150)
    avatar = models.ImageField(
        "avatar", upload_to="avatars/", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["username"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return str(self.email)


class Subscription(models.Model):
    """Foodgram subscription model"""

    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        ordering = ["from_user"]
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"