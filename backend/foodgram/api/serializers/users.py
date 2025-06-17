from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import UserModel
from recipes.models import RecipeModel
from api.serializers.fields import Base64Field


class ProfileUserSerializer(UserSerializer):
    """Сериализатор для профиля пользователя"""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "surname",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
                request is not None
                and not request.user.is_anonymous
                and obj.followers.filter(user=request.user).exists()
                and request.user.is_authenticated

        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class AvatarUserSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя"""

    avatar = Base64Field(required=True)

    def update(self, instance, validated_info):
        avatar = validated_info.get("avatar")
        if avatar is None:
            raise serializers.ValidationError("Avatar is necessary")

        instance.avatar = avatar
        instance.save()
        return instance

    class Meta:
        fields = ("avatar",)
        model = UserModel


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для коротких деталей"""

    class Meta:
        model = RecipeModel
        read_only_fields = ("id", "name", "image", "time_of_cooking")
        fields = read_only_fields


class RecipesWithUserSerializer(ProfileUserSerializer):
    """Сериализатор для рецептов пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(ProfileUserSerializer.Meta):
        fields = ProfileUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, user_obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit") if request else None
        recipes = user_obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data
