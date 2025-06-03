from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    IngredientRecipe,
    FavoriteRecipes,
    ShoppingCart,
)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe admin model"""

    list_display = ("name", "author")
    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__last_name",
    )
    list_filter = ("name", "author")
    inlines = (IngredientRecipeInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingredient admin model"""

    list_display = ("name", "measurement_unit")
    search_fields = ("name", "measurement_unit")
    list_filter = ("name", "measurement_unit")


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    """FavoriteRecipes admin model"""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ShoppingCart admin model"""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")