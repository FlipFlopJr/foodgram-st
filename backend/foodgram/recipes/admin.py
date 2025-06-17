from django.contrib import admin
from django.db.models import Min, Max
from django.utils.safestring import mark_safe

from .models import (
    IngredientModel,
    RecipeModel,
    RecipeIngredientModel,
    FavoriteRecipeModel,
    ShoppingCart,
)


class FilterOfTimeOfCooking(admin.SimpleListFilter):
    """Фильтр рецептов по времени приготовления"""

    title = "время приготовления"
    parameter_name = "time_of_cooking"

    def lookups(self, request, model_admin):
        stats = RecipeModel.objects.aggregate(
            min_time=Min("time_of_cooking"), max_time=Max("time_of_cooking")
        )

        if not stats["min_time"] or not stats["max_time"]:
            return []

        time_range = stats["max_time"] - stats["min_time"]
        threshold2 = stats["min_time"] + (2 * time_range) // 3
        threshold1 = stats["min_time"] + time_range // 3

        long_count = RecipeModel.objects.filter(time_of_cooking__gt=threshold2).count()

        medium_count = RecipeModel.objects.filter(
            time_of_cooking__gt=threshold1, time_of_cooking__lte=threshold2
        ).count()

        quick_count = RecipeModel.objects.filter(
            time_of_cooking__lte=threshold1
        ).count()

        return [
            ("quick", f"быстрее {threshold1} мин ({quick_count})"),
            ("medium", f"быстрее {threshold2} мин ({medium_count})"),
            ("long", f"дольше {threshold2} мин ({long_count})"),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        stats = RecipeModel.objects.aggregate(
            min_time=Min("time_of_cooking"), max_time=Max("time_of_cooking")
        )

        if not stats["min_time"] or not stats["max_time"]:
            return queryset

        time_range = stats["max_time"] - stats["min_time"]
        threshold1 = stats["min_time"] + time_range // 3
        threshold2 = stats["min_time"] + (2 * time_range) // 3

        if self.value() == "quick":
            return queryset.filter(time_of_cooking__lte=threshold1)
        if self.value() == "medium":
            return queryset.filter(
                time_of_cooking__gt=threshold1, time_of_cooking__lte=threshold2
            )
        if self.value() == "long":
            return queryset.filter(time_of_cooking__gt=threshold2)
        return queryset


class RecipeIngredientInline(admin.TabularInline):
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
    list_display = (
        "id",
        "name",
        "time_of_cooking",
        "author",
        "get_favorites_count",
        "get_ingredients",
        "get_image",
    )
    inlines = (RecipeIngredientInline,)
    list_filter = (FilterOfTimeOfCooking,)

    @admin.display(description="favorites")
    def get_favorites_count(self, obj):
        return obj.favoriterecipes.count()

    @admin.display(description="ingredients")
    @mark_safe
    def get_ingredients(self, obj):
        ingredients = obj.recipe_ingredients.all()
        ingredients_list = [
            f"{item.ingredient.name} - "
            f"{item.count} "
            f"{item.ingredient.unit_of_measure}"
            for item in ingredients
        ]
        return "<br>".join(ingredients_list)

    @admin.display(description="images")
    @mark_safe
    def get_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100">'
        return "Image is not found"


@admin.register(IngredientModel)
class AdminIngredientModel(admin.ModelAdmin):
    """Модель ингредиента админка"""

    list_filter = ("name", "unit_of_measure",)
    search_fields = ("name", "unit_of_measure")
    list_display = ("name", "unit_of_measure", "get_recipes_count")

    @admin.display(description="рецептов")
    def get_recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(FavoriteRecipeModel, ShoppingCart)
class RecipeUserRelationAdmiModel(admin.ModelAdmin):
    """Модель админки для отношений пользователь-рецепт"""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")
