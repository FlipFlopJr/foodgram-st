from django.shortcuts import redirect, get_object_or_404

from recipes.models import RecipeModel


def short_link_redirect(request, recipe_id):
    """Перенаправляет на рецепт"""
    recipe = get_object_or_404(RecipeModel, id=recipe_id)
    return redirect(f"/recipes/{recipe.id}/")
