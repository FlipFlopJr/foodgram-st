from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class UserModel(AbstractUser):
    """Модель пользователя"""

    first_name = models.CharField("name", max_length=150)
    last_name = models.CharField("last_name", max_length=150)
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

    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
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


class RecipeModel(models.Model):
    """Модель рецептов"""

    author = models.ForeignKey(
        UserModel,
        verbose_name="author",
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name="description")
    name = models.CharField("name", max_length=256)
    ingredients = models.ManyToManyField(
        "IngredientModel",
        through="RecipeIngredientModel",
        verbose_name="ingredients",
        related_name="recipes",
    )
    cooking_time = models.PositiveIntegerField(
        "time of cooking (minutes)",
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField("image", upload_to="recipes/")

    class Meta:
        verbose_name = "recipe"
        verbose_name_plural = "recipes"
        ordering = ("name",)

    def __str__(self):
        return self.name


class IngredientModel(models.Model):
    """Модель ингредиентов"""

    name = models.CharField(
        "name",
        max_length=256,
        unique=True,
    )
    measurement_unit = models.CharField(
        "unit of measure",
        max_length=256,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class RecipeIngredientModel(models.Model):
    """Модель отношения многие ко многим между рецептами и ингредиентами"""

    recipe = models.ForeignKey(
        RecipeModel,
        related_name="recipe_ingredients",
        verbose_name="recipe",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        IngredientModel,
        related_name="recipe_ingredients",
        verbose_name="ingredient",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        "amount",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["recipe", "ingredient"]
        verbose_name = "ingredient recipe"
        verbose_name_plural = "ingredient recipes"

    def __str__(self):
        return (
            f"{self.ingredient} - "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class RecipeUserRelationModel(models.Model):
    """Модель отношений пользователя с рецептами"""

    user = models.ForeignKey(
        UserModel,
        verbose_name="user",
        related_name="%(class)s_relations",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        RecipeModel,
        verbose_name="recipe",
        related_name="%(class)s_relations",
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_%(class)s"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class FavoriteRecipeModel(RecipeUserRelationModel):
    """Модель для любимых рецептов"""

    class Meta:
        verbose_name = "favorite recipe"
        verbose_name_plural = "favorite recipes"


class ShoppingCart(RecipeUserRelationModel):
    """Модель для корзины пользователя"""

    class Meta:
        verbose_name = "shopping cart item"
        verbose_name_plural = "shopping cart items"
