from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator


class UserModel(AbstractUser):
    """Пользовательская модель пользователя"""

    first_name = models.CharField("First Name", max_length=150)
    last_name = models.CharField("Last Name", max_length=150)
    avatar = models.ImageField("Avatar", upload_to="avatars/", blank=True, null=True)
    email = models.EmailField("Email", unique=True, max_length=254)
    username = models.CharField(
        "Username",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Username must contain only letters, digits and @/./+/-/_",
                code="invalid_username",
            )
        ],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["username"]

    def __str__(self):
        return self.email


class SubscriptionModel(models.Model):
    """Подписка пользователя на автора"""

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Subscriber",
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="authors",
        verbose_name="Author",
    )

    class Meta:
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(fields=["user", "author"], name="unique_subscription")
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"


class IngredientModel(models.Model):
    """Ингредиент"""

    name = models.CharField("Name", max_length=256, unique=True)
    measurement_unit = models.CharField("Unit of measure", max_length=256)

    class Meta:
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class RecipeModel(models.Model):
    """Рецепт"""

    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Author",
    )
    name = models.CharField("Name", max_length=256)
    text = models.TextField("Description")
    ingredients = models.ManyToManyField(
        IngredientModel,
        through="RecipeIngredientModel",
        related_name="recipes",
        verbose_name="Ingredients",
    )
    cooking_time = models.PositiveIntegerField(
        "Cooking time (minutes)", validators=[MinValueValidator(1)]
    )
    image = models.ImageField("Image", upload_to="recipes/")

    class Meta:
        verbose_name = "recipe"
        verbose_name_plural = "recipes"
        ordering = ("name",)

    def __str__(self):
        return self.name


class RecipeIngredientModel(models.Model):
    """Связь между рецептами и ингредиентами с указанием количества"""

    recipe = models.ForeignKey(
        RecipeModel,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Recipe",
    )
    ingredient = models.ForeignKey(
        IngredientModel,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ingredient",
    )
    amount = models.PositiveIntegerField("Amount", validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "ingredient in recipe"
        verbose_name_plural = "ingredients in recipes"
        ordering = ["recipe", "ingredient"]

    def __str__(self):
        return f"{self.ingredient} - {self.amount} {self.ingredient.measurement_unit}"


class RecipeUserRelationModel(models.Model):
    """Абстрактная модель отношений пользователя с рецептом"""

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="%(class)s_relations",
        verbose_name="User",
    )
    recipe = models.ForeignKey(
        RecipeModel,
        on_delete=models.CASCADE,
        related_name="%(class)s_relations",
        verbose_name="Recipe",
    )

    class Meta:
        abstract = True
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_%(class)s")
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class FavoriteRecipeModel(RecipeUserRelationModel):
    """Любимые рецепты пользователя"""

    class Meta:
        verbose_name = "favorite recipe"
        verbose_name_plural = "favorite recipes"


class ShoppingCart(RecipeUserRelationModel):
    """Элементы корзины пользователя"""

    class Meta:
        verbose_name = "shopping cart item"
        verbose_name_plural = "shopping cart items"
