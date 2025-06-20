from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import Http404, FileResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import RecipeModel, FavoriteRecipeModel, ShoppingCart
from api.serializers.recipes import (
    ReadRecipeSerializer,
    WriteRecipeSerializer,
)
from api.serializers.users import ShortRecipeSerializer
from api.permissions import ReadOnlyOrIsAuthor
from api.pagination import PaginationClass
from api.filters import FilterRecipeModel


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = RecipeModel.objects.all()
    filterset_class = FilterRecipeModel
    pagination_class = PaginationClass
    filter_backends = [DjangoFilterBackend]
    permission_classes = (ReadOnlyOrIsAuthor,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated("Требуется авторизация для создания рецепта")
        serializer.save(author=user)

    @action(methods=["get"], detail=True, url_path="get-link")
    def get_link_to_recipe(self, request, pk):
        if not RecipeModel.objects.filter(pk=pk).exists():
            raise Http404

        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("recipes:short-link-redirect", args=[pk])
                )
            }
        )

    def _handle_recipe_relation(self,
                                request, recipe_id, model_class, already_exists_message
                                ):

        recipe = get_object_or_404(RecipeModel, pk=recipe_id)

        current_user = request.user

        if request.method == "POST":
            _, created = model_class.objects.get_or_create(
                user=current_user, recipe=recipe
            )

            if not created:
                raise ValidationError({"errors": already_exists_message})

            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )

        get_object_or_404(
            model_class, user=current_user, recipe=recipe
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._handle_recipe_relation(
            request, pk, FavoriteRecipeModel, "Recipe is already favorited"
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_recipe_relation(
            request, pk, ShoppingCart, "recipe is already in shopping cart"
        )

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def download_shopping_cart(self, request):

        recipes = RecipeModel.objects.filter(shoppingcart_relations__user=request.user)

        if not recipes.exists():
            raise ValidationError({"errors": "Shopping cart is empty"})

        ingredients = (
            recipes.values(
                "ingredients__name", "ingredients__measurement_unit"
            )
            .annotate(total_amount=Sum("recipe_ingredients__amount"))
            .order_by("ingredients__name")
        )

        current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        shopping_list = [
            "Foodgram - Shopping Cart",
            f"Date: {current_date} UTC",
            f"User: {request.user.username}",
            "",
            "Ingredients:",
        ]

        for i, ingredient in enumerate(ingredients, 1):
            shopping_list.append(
                f"{i}. {ingredient['ingredients__name'].title()} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredients__measurement_unit']}"
            )

        shopping_list.append("")
        shopping_list.append("Recipes:")

        for recipe in recipes:
            shopping_list.append(
                f"- {recipe.name} (Author: {recipe.author.get_full_name()})"
            )

        shopping_list.append("")
        shopping_list.append(
            f"Foodgram - Your cooking helper © {datetime.now().year}"
        )

        return FileResponse(
            ("\n".join(shopping_list)),
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain; charset=utf-8",
        )

    def get_queryset(self):
        queryset = RecipeModel.objects.all()
        user = self.request.user
        request = self.request
        is_in_shopping_cart = request.query_params.get("is_in_shopping_cart")

        # Если is_in_shopping_cart=1 и пользователь авторизован
        if is_in_shopping_cart in ("1", "true", "True") and user.is_authenticated:
            queryset = queryset.filter(shoppingcart_relations__user=user)

        return queryset
