from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from recipes.models import RecipeModel, RecipeIngredientModel
from api.serializers.users import ProfileUserSerializer
from api.serializers.ingredients import (
    IngredientRecipeReadSerializer,
    IngredientRecipeWriteSerializer,
)
from api.serializers.fields import Base64Field

User = get_user_model()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения сокращенных деталей"""

    class Meta:
        model = RecipeModel
        fields = ("id", "name", "image", "time_of_cooking")


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения деталей рецепта"""

    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    ingredients = IngredientRecipeReadSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    author = ProfileUserSerializer(read_only=True)

    class Meta:
        model = RecipeModel
        read_only_fields = (
            "id",
            "author",
            "ingredients",
            "is_in_shopping_cart",
            "is_favorite",
            "name",
            "image",
            "text",
            "time_of_cooking",
        )
        fields = read_only_fields

    def _verify_relation_presence(self, recipe_object, relation_name):
        request = self.context.get("request")
        return (
                request
                and getattr(recipe_object, relation_name)
                .filter(user=request.user)
                .exists()
                and request.user.is_authenticated

        )

    def get_is_favorite(self, recipe_object):
        return self._verify_relation_presence(recipe_object, "favoriterecipes")

    def get_is_in_shopping_cart(self, recipe_object):
        return self._verify_relation_presence(recipe_object, "shoppingcarts")


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для записи деталей рецепта"""

    image = Base64Field()
    time_of_cooking = serializers.IntegerField(min_value=1)
    ingredients = IngredientRecipeWriteSerializer(many=True, required=True)

    class Meta:
        model = RecipeModel
        fields = (
            "id",
            "ingredients",
            "image",
            "name",
            "text",
            "time_of_cooking",
        )

    def validate(self, info):
        if "ingredients" not in info and self.instance:
            raise serializers.ValidationError(
                {"ingredients": "This field is necessary."}
            )
        return info

    def validate_ingredients(self, ingredients_info):
        if not ingredients_info:
            raise serializers.ValidationError(
                {"ingredients": "Please fill in this field."}
            )

        ingredient_ids = [item["ingredient"] for item in ingredients_info]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Duplicate values are not permitted."}
            )

        return ingredients_info

    def _create_ingredients_recipe(self, recipe, ingredients_info):
        RecipeIngredientModel.objects.bulk_create(
            [
                RecipeIngredientModel(
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                    recipe=recipe
                )
                for ingredient_data in ingredients_info
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_info = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self._create_ingredients_recipe(recipe, ingredients_info)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_info = validated_data.pop("ingredients")
        instance.recipe_ingredients.all().delete()
        self._create_ingredients_recipe(instance, ingredients_info)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return ReadRecipeSerializer(recipe, context=self.context).data
