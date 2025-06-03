from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(models.Model):
    """Recipe model"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="author",
    )
    name = models.CharField("name", max_length=256)
    text = models.TextField(verbose_name="description")
    ingredients = models.ManyToManyField(
        "ingredient",
        through="IngredientRecipe",
        related_name="recipes",
        verbose_name="ingredients",
    )
    cooking_time = models.PositiveIntegerField(
        "cooking time (minutes)",
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField("image", upload_to="recipes/")

    class Meta:
        ordering = ["name"]
        verbose_name = "recipe"
        verbose_name_plural = "recipes"

    def __str__(self):
        return str(self.name)


class Ingredient(models.Model):
    """Ingredient model"""

    name = models.CharField(
        "name",
        max_length=256,
        unique=True,
    )
    measurement_unit = models.CharField(
        "measurement unit",
        max_length=256,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class IngredientRecipe(models.Model):
    """Many to many relationship between Recipe and Ingredient"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="recipe",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="ingredient",
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


class UserRecipeRelation(models.Model):
    """Model for user recipe relations"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="user",
        related_name="%(class)s_relations",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="recipe",
        related_name="%(class)s_relations",
    )

    class Meta:
        abstract = True
        ordering = ["user", "recipe"]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class FavoriteRecipes(UserRecipeRelation):
    """Model for favorite recipes"""

    class Meta:
        verbose_name = "favorite recipe"
        verbose_name_plural = "favorite recipes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_recipe_favorite"
            )
        ]


class ShoppingCart(UserRecipeRelation):
    """Model for shopping cart items"""

    class Meta:
        verbose_name = "shopping cart item"
        verbose_name_plural = "shopping cart items"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_shopping_cart",
            )
        ]