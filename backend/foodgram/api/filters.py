from django_filters.rest_framework import FilterSet, filters

from recipes.models import IngredientModel, RecipeModel


class FilterIngredientModel(FilterSet):
    """Фильтр для модели ингридиентов"""

    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = IngredientModel
        fields = ["name", ]


class FilterRecipeModel(FilterSet):
    """Фильтр для модели рецептов"""
    author = filters.NumberFilter(field_name="author__id")
    shopping_cart = filters.BooleanFilter(
        method="filter_of_shopping_cart"
    )
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")

    class Meta:
        model = RecipeModel
        fields = ["author", "is_favorited", "shopping_cart"]

    def filter_is_favorited(self, recipes, name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            return recipes.filter(favoriterecipemodel_relations__user=current_user)
        return recipes

    def filter_of_shopping_cart(self, recipes, name, value):
        current_user = self.request.user
        if current_user.is_authenticated and value:
            return recipes.filter(shoppingcart_relations__user=current_user)
        return recipes
