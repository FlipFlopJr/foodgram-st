from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating ingredients"""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for reading ingredient recipes"""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing ingredient recipes"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient",
    )
    amount = serializers.IntegerField(
        required=True,
        min_value=1,
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")