from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import UserModel
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

    def get_is_subscription(self, obj):
        request = self.context.get("request")
        if (
                request is None
                or not request.user.is_authenticated
                or request.user.is_anonymous
        ):
            return False
        return obj.followers.filter(from_user=request.user).exists()

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
