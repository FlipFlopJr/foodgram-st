from rest_framework import serializers

from recipes.models import IngredientModel, RecipeIngredientModel


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения ингредиентов"""

    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = IngredientModel


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецептов"""

    id = serializers.IntegerField(source="ingredient.id")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )
    name = serializers.CharField(source="ingredient.name")

    class Meta:
        model = RecipeIngredientModel
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов и рецептов"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=IngredientModel.objects.all(),
        source="ingredient",
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=1,
    )

    class Meta:
        model = RecipeIngredientModel
        fields = ("id", "amount")
