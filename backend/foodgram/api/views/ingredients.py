from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import IngredientModel
from api.serializers.ingredients import IngredientSerializer
from api.filters import FilterIngredientModel


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientModel.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FilterIngredientModel
    pagination_class = None
