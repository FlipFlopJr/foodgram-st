from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from api.pagination import PaginationSite
from api.serializers.users import ProfileUserSerializer, AvatarUserSerializer
from api.serializers.subscriptions import RecipesWithUserSerializer

from users.models import UserModel, SubscriptionModel


class UserViewset(DjoserUserViewSet):
    """Вьюсет пользователя"""

    queryset = UserModel.objects.all()
    pagination_class = PaginationSite
    serializer_class = ProfileUserSerializer

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
            serializer = AvatarUserSerializer(
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
        serializer_class=RecipesWithUserSerializer,
        pagination_class=PaginationSite,
    )
    def subscriptions(self, request):
        queryset = UserModel.objects.filter(followers__user_from=request.user)
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
        serializer_class=RecipesWithUserSerializer,
    )
    def subscribe(self, request, id=None):
        user_to = get_object_or_404(UserModel, id=id)
        current_user = request.user

        if request.method == "POST":
            if current_user == user_to:
                return Response(
                    {"errors": "Cannot subscribe to yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription, created = SubscriptionModel.objects.get_or_create(
                user_from=current_user, user_to=user_to
            )

            if not created:
                return Response(
                    {"errors": "You are already subscribed to this user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(user_to)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not SubscriptionModel.objects.filter(
                user_from=current_user, user_to=user_to
        ).exists():
            return Response(
                {"errors": "You are not subscribed to this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SubscriptionModel.objects.filter(
            user_from=current_user, user_to=user_to
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
