from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import IngredientModel
from api.filters import FilterIngredientModel
from api.serializers.ingredients import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    queryset = IngredientModel.objects.all()
    filterset_class = FilterIngredientModel
    filter_backends = [DjangoFilterBackend]
    pagination_class = None
