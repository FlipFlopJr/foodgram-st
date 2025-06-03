from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.serializers.recipes import RecipeShortSerializer


User = get_user_model()


class UserWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с его рецептами."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if (
            request is None
            or request.user.is_anonymous
            or not request.user.is_authenticated
        ):
            return False
        return obj.followers.filter(from_user=request.user).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_avatar(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None