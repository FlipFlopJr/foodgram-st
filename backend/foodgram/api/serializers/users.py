from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import User
from api.serializers.fields import Base64ImageField


class UserProfileSerializer(UserSerializer):
    """Serializer for user profile"""

    is_subscribed = serializers.SerializerMethodField()
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

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class UserAvatarSerializer(serializers.ModelSerializer):
    """Serializer for user avatar"""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def update(self, instance, validated_data):
        avatar = validated_data.get("avatar")
        if avatar is None:
            raise serializers.ValidationError("Avatar is required")

        instance.avatar = avatar
        instance.save()
        return instance