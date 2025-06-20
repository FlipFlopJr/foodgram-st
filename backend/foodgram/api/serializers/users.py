from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import UserModel, RecipeModel
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
            "last_name",
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
        read_only_fields = ("id", "name", "image", "cooking_time")
        fields = read_only_fields


class RecipesWithUserSerializer(ProfileUserSerializer):
    """Сериализатор для рецептов пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_amount = serializers.IntegerField(
        source="recipes.amount", read_only=True
    )

    class Meta(ProfileUserSerializer.Meta):
        fields = ProfileUserSerializer.Meta.fields + (
            "recipes",
            "recipes_amount",
        )

    def get_recipes(self, user_obj):
        return ShortRecipeSerializer(
            user_obj.recipes.all()[
            : int(
                self.context.get("request").GET.get(
                    "recipes_limit", 10 ** 10
                )
            )
            ],
            many=True,
        ).data


from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import UserModel, RecipeModel
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
            "last_name",
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
        read_only_fields = ("id", "name", "image", "cooking_time")
        fields = read_only_fields


class RecipesWithUserSerializer(ProfileUserSerializer):
    """Сериализатор для рецептов пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_amount = serializers.IntegerField(
        source="recipes.amount", read_only=True
    )

    class Meta(ProfileUserSerializer.Meta):
        fields = ProfileUserSerializer.Meta.fields + (
            "recipes",
            "recipes_amount",
        )

    def get_recipes(self, user_obj):
        return ShortRecipeSerializer(
            user_obj.recipes.all()[
            : int(
                self.context.get("request").GET.get(
                    "recipes_limit", 10 ** 10
                )
            )
            ],
            many=True,
        ).data
