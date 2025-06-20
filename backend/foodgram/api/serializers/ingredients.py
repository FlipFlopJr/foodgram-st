from rest_framework import serializers

from recipes.models import IngredientModel, RecipeIngredientModel


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и редактирования ингредиентов"""

    class Meta:
        model = IngredientModel
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте"""

    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit",
                                             read_only=True)

    class Meta:
        model = RecipeIngredientModel
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт"""

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        queryset=IngredientModel.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredientModel
        fields = ("id", "amount")
