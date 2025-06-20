from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.pagination import PaginationClass
from api.serializers.users import ProfileUserSerializer, AvatarUserSerializer, RecipesWithUserSerializer
from recipes.models import UserModel, SubscriptionModel


class UserViewset(DjoserUserViewSet):
    """
    Вьюсет для работы с пользователями.
    Расширяет стандартный UserViewSet из djoser, добавляя кастомные действия:
    """
    queryset = UserModel.objects.all()
    serializer_class = ProfileUserSerializer
    permission_classes = [AllowAny]
    pagination_class = PaginationClass

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Возвращает данные текущего аутентифицированного пользователя."""
        return super().me(request)

    @action(
        detail=False,
        methods=["put", "delete"],
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        user = request.user

        if request.method == "PUT":
            serializer = AvatarUserSerializer(
                user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"avatar": user.avatar.url}, status=status.HTTP_200_OK)

        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=RecipesWithUserSerializer,
        pagination_class=PaginationClass,
    )
    def subscriptions(self, request):
        subscribed_qs = UserModel.objects.filter(authors__user=request.user).prefetch_related("recipes")
        page = self.paginate_queryset(subscribed_qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        serializer_class=RecipesWithUserSerializer,
    )
    def subscribe(self, request, id=None):

        author = get_object_or_404(UserModel, id=id)
        user = request.user

        if request.method == "POST":
            if user == author:
                raise ValidationError("You cannot subscribe to yourself.")

            subscription, created = SubscriptionModel.objects.get_or_create(user=user, author=author)
            if not created:
                raise ValidationError("Subscription already exists.")

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(SubscriptionModel, user=user, author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
