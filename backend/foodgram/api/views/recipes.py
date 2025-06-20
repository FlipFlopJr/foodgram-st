from datetime import datetime
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import Http404, FileResponse
from django.db.models import Sum

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import RecipeModel, FavoriteRecipeModel, ShoppingCart
from api.serializers.recipes import ReadRecipeSerializer, WriteRecipeSerializer
from api.serializers.users import ShortRecipeSerializer
from api.permissions import ReadOnlyOrIsAuthor
from api.pagination import PaginationClass
from api.filters import FilterRecipeModel


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = RecipeModel.objects.all()
    filterset_class = FilterRecipeModel
    pagination_class = PaginationClass
    filter_backends = [DjangoFilterBackend]
    permission_classes = [ReadOnlyOrIsAuthor]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated:
            raise NotAuthenticated(detail="Требуется авторизация для создания рецепта")
        serializer.save(author=user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link_to_recipe(self, request, pk=None):
        recipe_exists = RecipeModel.objects.filter(pk=pk).exists()
        if not recipe_exists:
            raise Http404

        short_url = request.build_absolute_uri(
            reverse('recipes:short-link-redirect', args=[pk]))
        return Response({'short-link': short_url})

    def _modify_recipe_relation(self, request, recipe_id, relation_model, error_msg):
        recipe = get_object_or_404(RecipeModel, pk=recipe_id)
        user = request.user

        if request.method == 'POST':
            obj, created = relation_model.objects.get_or_create(user=user, recipe=recipe)
            if not created:
                raise ValidationError({'errors': error_msg})
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        obj = get_object_or_404(relation_model, user=user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._modify_recipe_relation(request,
                                            pk,
                                            FavoriteRecipeModel,
                                            "Recipe is already favorited")

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._modify_recipe_relation(request,
                                            pk,
                                            ShoppingCart,
                                            "Recipe is already in shopping cart")

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        recipes = RecipeModel.objects.filter(shoppingcart_relations__user=user)
        if not recipes.exists():
            raise ValidationError({'errors': 'Shopping cart is empty'})

        aggregated_ingredients = (
            recipes.values('ingredients__name', 'ingredients__measurement_unit')
            .annotate(total_amount=Sum('recipe_ingredients__amount'))
            .order_by('ingredients__name')
        )

        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "Foodgram - Shopping Cart",
            f"Date: {current_time} UTC",
            f"User: {user.username}",
            "",
            "Ingredients:",
        ]

        for idx, ingredient in enumerate(aggregated_ingredients, start=1):
            lines.append(
                f"{idx}. {ingredient['ingredients__name'].title()} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredients__measurement_unit']}"
            )

        lines.extend([
            "",
            "Recipes:",
        ])

        for recipe in recipes:
            lines.append(f"- {recipe.name} (Author: {recipe.author.get_full_name()})")

        lines.extend([
            "",
            f"Foodgram - Your cooking helper © {datetime.now().year}"
        ])

        content = "\n".join(lines)

        return FileResponse(
            content,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8',
        )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        param = self.request.query_params.get('is_in_shopping_cart')

        if param and param.lower() in ('1', 'true') and user.is_authenticated:
            qs = qs.filter(shoppingcart_relations__user=user)

        return qs
