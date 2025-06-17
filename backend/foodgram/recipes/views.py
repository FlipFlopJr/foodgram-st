from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404

from .models import RecipeModel


def redirect_short_link(request, recipe_id):
    """Перенаправляет на рецепт"""
    get_object_or_404(RecipeModel, id=recipe_id)
    return redirect(f"/api/recipes/{recipe_id}/")
