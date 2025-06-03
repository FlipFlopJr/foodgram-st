from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from recipes.models import Recipe, IngredientRecipe
from api.serializers.users import UserProfileSerializer
from api.serializers.ingredients import (
    IngredientRecipeReadSerializer,
    IngredientRecipeWriteSerializer,
)
from api.serializers.fields import Base64ImageField


User = get_user_model()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Serializer for short recipe details."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for reading recipe details."""

    author = UserProfileSerializer(read_only=True)
    ingredients = IngredientRecipeReadSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.favoriterecipes_relations.filter(
                user=request.user
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.shoppingcart_relations.filter(
                user=request.user
            ).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing recipe details."""

    ingredients = IngredientRecipeWriteSerializer(many=True, required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                {"ingredients": "Cannot be empty."}
            )

        ingredient_ids = [item["ingredient"].id for item in value]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Cannot contain duplicates."}
            )

        return value

    def validate(self, data):
        if self.instance and "ingredients" not in data:
            raise serializers.ValidationError(
                {"ingredients": "This field is required."}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_data["ingredient"],
                amount=ingredient_data["amount"],
            )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)

        instance = super().update(instance, validated_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()

            for ingredient_data in ingredients_data:
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                )

        return instance