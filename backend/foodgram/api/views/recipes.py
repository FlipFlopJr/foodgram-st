from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum

from recipes.models import Recipe, FavoriteRecipes, ShoppingCart
from api.serializers.recipes import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
    RecipeShortSerializer,
)
from api.permissions import IsAuthorOrStaffOrReadOnly
from api.pagination import CustomPagination
from api.filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    pagination_class = CustomPagination
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ["list", "retrieve", "get_link_to_recipe"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAuthorOrStaffOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        read_serializer = RecipeReadSerializer(
            instance=write_serializer.instance,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        write_serializer = self.get_serializer(
            recipe, data=request.data, partial=True
        )
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)
        read_serializer = RecipeReadSerializer(
            instance=write_serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(read_serializer.data)

    @action(methods=["get"], detail=True, url_path="get-link")
    def get_link_to_recipe(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        relative_link = reverse("short-link-redirect", args=[recipe.id])
        absolute_link = request.build_absolute_uri(relative_link)

        return Response({"short-link": absolute_link})

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        current_user = request.user

        if request.method == "POST":
            _, created = FavoriteRecipes.objects.get_or_create(
                user=current_user, recipe=recipe
            )

            if not created:
                return Response(
                    {"errors": "Recipe already in favorites"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not FavoriteRecipes.objects.filter(user=current_user, recipe=recipe).exists():
            return Response(
                {"errors": "Recipe is not in favorites"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FavoriteRecipes.objects.filter(user=current_user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == "POST":
            _, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                return Response(
                    {"errors": "Recipe already in shopping cart"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": "Recipe is not in shopping cart"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(
            shoppingcart_relations__user=request.user
        )

        if not recipes.exists():
            return Response(
                {"errors": "Shopping cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            recipes.values(
                "ingredients__name", "ingredients__measurement_unit"
            )
            .annotate(total_amount=Sum("recipe_ingredients__amount"))
            .order_by("ingredients__name")
        )

        current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        shopping_list = [
            "Foodgram - Shopping List",
            f"Date: {current_date} UTC",
            f"User: {request.user.username}",
            "",
            "Ingredients:",
        ]

        for i, ingredient in enumerate(ingredients, 1):
            shopping_list.append(
                f"{i}. {ingredient['ingredients__name']} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredients__measurement_unit']}"
            )

        shopping_list.append("")
        shopping_list.append(
            f"Foodgram - Your Recipes Helper © {datetime.now().year}"
        )

        response = HttpResponse(
            "\n".join(shopping_list), content_type="text/plain; charset=utf-8"
        )
        response["Content-Disposition"] = (
            "attachment; " 'filename="shopping_list.txt"'
        )

        return response