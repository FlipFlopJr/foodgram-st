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

from recipes.models import RecipeModel, FavoriteRecipeModel, ShoppingCart
from api.serializers.recipes import (
    ReadRecipeSerializer,
    WriteRecipeSerializer,
    ShortRecipeSerializer,
)
from api.permissions import IsStaffOrAuthorOrReadOnly
from api.pagination import PaginationSite
from api.filters import FilterRecipeModel


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = RecipeModel.objects.all()
    filterset_class = FilterRecipeModel
    pagination_class = PaginationSite
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "get_link_to_recipe"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsStaffOrAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        read_serializer = ReadRecipeSerializer(
            context=self.get_serializer_context(),
            instance=write_serializer.instance
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
        read_serializer = ReadRecipeSerializer(
            context=self.get_serializer_context(),
            instance=write_serializer.instance,
        )
        return Response(read_serializer.data)

    @action(methods=["get"], detail=True, url_path="get-link")
    def get_link_to_recipe(self, request, pk):
        recipe = get_object_or_404(RecipeModel, pk=pk)
        relative_link = reverse("short-link-redirect", args=[recipe.id])
        absolute_link = request.build_absolute_uri(relative_link)

        return Response({"short-link": absolute_link})

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        current_user = request.user
        recipe = get_object_or_404(RecipeModel, pk=pk)

        if request.method == "POST":
            _, created = FavoriteRecipeModel.objects.get_or_create(
                user=current_user, recipe=recipe
            )

            if not created:
                return Response(
                    {"errors": "You’ve already added this recipe to favorites."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not FavoriteRecipeModel.objects.filter(user=current_user, recipe=recipe).exists():
            return Response(
                {"errors": "You haven’t added this recipe to favorites yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        FavoriteRecipeModel.objects.filter(user=current_user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(RecipeModel, id=pk)
        user = request.user

        if request.method == "POST":
            _, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )

            if not created:
                return Response(
                    {"errors": "You've already added this recipe to your cart."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": "Recipe not added to cart yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def shopping_cart_download(self, request):
        recipes = RecipeModel.objects.filter(
            shoppingcart_relations__user=request.user
        )

        if not recipes.exists():
            return Response(
                {"errors": "Cart is currently empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            recipes.values(
                "ingredients__name", "ingredients__unit_of_measure"
            )
            .annotate(total_amount=Sum("recipe_ingredients__count"))
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
                f"{ingredient['ingredients__unit_of_measure']}"
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
