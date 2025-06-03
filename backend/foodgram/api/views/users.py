from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.serializers.users import UserProfileSerializer, UserAvatarSerializer
from api.serializers.subscriptions import UserWithRecipesSerializer

from users.models import User, Subscription


class UserViewSet(DjoserUserViewSet):
    """User viewset"""

    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        allow_any_actions = set(["retrieve"])
        if self.action in allow_any_actions:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    @action(
        methods=["put", "delete"],
        detail=False,
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        current_user = request.user
        if request.method == "PUT":
            serializer = UserAvatarSerializer(
                current_user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": current_user.avatar.url}, status=status.HTTP_200_OK
            )

        if current_user.avatar:
            current_user.avatar.delete()
            current_user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
        pagination_class=CustomPagination,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(followers__from_user=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id=None):
        to_user = get_object_or_404(User, id=id)
        current_user = request.user

        if request.method == "POST":
            if current_user == to_user:
                return Response(
                    {"errors": "Cannot subscribe to yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription, created = Subscription.objects.get_or_create(
                from_user=current_user, to_user=to_user
            )

            if not created:
                return Response(
                    {"errors": "You are already subscribed to this user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(to_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Subscription.objects.filter(
            from_user=current_user, to_user=to_user
        ).exists():
            return Response(
                {"errors": "You are not subscribed to this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.filter(
            from_user=current_user, to_user=to_user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)