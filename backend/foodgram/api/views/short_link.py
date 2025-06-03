from django.shortcuts import redirect, get_object_or_404

from recipes.models import Recipe


def redirect_short_link(request, recipe_id):
    """Redirects to the recipe"""
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return redirect(f"/recipes/{recipe.id}/")