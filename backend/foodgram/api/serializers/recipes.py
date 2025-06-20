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


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения деталей рецепта"""

    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
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
            "is_favorited",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        fields = read_only_fields

    def _verify_relation_presence(self, recipe_object, relation_name):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return getattr(recipe_object, relation_name).filter(user=user).exists()

    def get_is_favorited(self, recipe_object):
        return self._verify_relation_presence(recipe_object,
                                              "favoriterecipemodel_relations")

    def get_is_in_shopping_cart(self, recipe_object):
        return self._verify_relation_presence(recipe_object, "shoppingcart_relations")


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для записи деталей рецепта"""

    image = Base64Field()
    cooking_time = serializers.IntegerField(min_value=1)
    ingredients = IngredientRecipeWriteSerializer(many=True, required=True)

    class Meta:
        model = RecipeModel
        fields = (
            "id",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
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

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredientModel.objects.bulk_create(
            [
                RecipeIngredientModel(
                    recipe=recipe,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"]
                )
                for ingredient_data in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_info = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self._create_recipe_ingredients(recipe, ingredients_info)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_info = validated_data.pop("ingredients")
        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients_info)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return ReadRecipeSerializer(recipe, context=self.context).data
