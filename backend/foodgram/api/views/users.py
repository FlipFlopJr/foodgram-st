from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from api.pagination import PaginationClass
from api.serializers.users import ProfileUserSerializer, AvatarUserSerializer, RecipesWithUserSerializer

from recipes.models import UserModel, SubscriptionModel


class UserViewset(DjoserUserViewSet):
    """Вьюсет пользователя"""

    queryset = UserModel.objects.all()
    permission_classes = [AllowAny]
    pagination_class = PaginationClass
    serializer_class = ProfileUserSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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
        pagination_class=PaginationClass,
    )
    def subscriptions(self, request):
        subscribed_users = UserModel.objects.filter(
            authors__user=request.user
        ).prefetch_related("recipes")
        paginated_users = self.paginate_queryset(subscribed_users)
        serializer = self.get_serializer(paginated_users, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        serializer_class=RecipesWithUserSerializer,
    )
    def subscribe(self, request, id=None):
        from rest_framework.exceptions import ValidationError

        author = get_object_or_404(UserModel, id=id)
        current_user = request.user

        if request.method == "POST":
            if current_user == author:
                raise ValidationError("You can't subscribe to yourself")

            subscription, created = SubscriptionModel.objects.get_or_create(
                user=current_user, author=author
            )

            if not created:
                raise ValidationError(
                    "You have already subscribed to this user"

                )

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = SubscriptionModel.objects.filter(
            user=current_user, author=author
        ).first()

        if not subscription:
            raise ValidationError("You haven't subscribed to this user yet")

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
