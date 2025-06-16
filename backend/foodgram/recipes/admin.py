from django.contrib import admin

from .models import (
    IngredientModel,
    RecipeModel,
    RecipeIngredientModel,
    FavoriteRecipeModel,
    ShoppingCart,
)


class IngredientRecipeInline(admin.TabularInline):
    model = RecipeIngredientModel
    extra = 1


@admin.register(RecipeModel)
class AdminRecipeModel(admin.ModelAdmin):
    """Модель рецепта админка"""

    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__surname",
    )
    list_display = ("name", "author")
    inlines = (IngredientRecipeInline,)
    list_filter = ("name", "author")


@admin.register(IngredientModel)
class AdminIngredientModel(admin.ModelAdmin):
    """Модель ингредиента админка"""

    list_filter = ("name", "unit_of_measure")
    search_fields = ("name", "unit_of_measure")
    list_display = ("name", "unit_of_measure")


@admin.register(FavoriteRecipeModel)
class AdminFavoriteRecipesModel(admin.ModelAdmin):
    """Модель любимых рецептов админка"""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")


@admin.register(ShoppingCart)
class AdminShoppingCartModel(admin.ModelAdmin):
    """Модель корзины админка"""

    list_filter = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_display = ("user", "recipe")
