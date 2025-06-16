from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.serializers.recipes import ShortRecipeSerializer

User = get_user_model()


class RecipesWithUserSerializer(serializers.ModelSerializer):
    """Пользователяьский сериализатор с его рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "surname",
            "recipes",
            "recipes_count",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscription(self, obj):
        request = self.context.get("request")
        if (
                request is None
                or not request.user.is_authenticated
                or request.user.is_anonymous
        ):
            return False
        return obj.followers.filter(from_user=request.user).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        limit = request.query_params.get("recipes_limit")
        if limit:
            recipes = recipes[: int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None
