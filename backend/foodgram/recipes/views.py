from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, get_object_or_404

from .models import RecipeModel


def redirect_short_link(request, recipe_id):
    """Перенаправляет на рецепт"""
    if not RecipeModel.objects.filter(id=recipe_id).exists():
        raise ValidationError(f"Рецепт с id={recipe_id} не существует")
    return redirect(f"/recipes/{recipe_id}/")
