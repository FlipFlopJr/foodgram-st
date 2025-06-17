from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from api.views.users import UserViewset
from api.views.ingredients import IngredientViewSet
from api.views.recipes import RecipeViewSet

router = DefaultRouter()
router.register(r"users", UserViewset, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('users-list', request=request, format=format),
        'ingredients': reverse('ingredients-list', request=request, format=format),
        'recipes': reverse('recipes-list', request=request, format=format),
    })


urlpatterns = [
    path("", api_root, name='api-root'),
    path("", include(router.urls)),
]