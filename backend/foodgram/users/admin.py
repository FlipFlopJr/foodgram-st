from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from users.models import UserModel, SubscriptionModel


class UserHasRecipesFilter(admin.SimpleListFilter):
    title = "presence of recipes"
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return (
            ("no", "Нет рецептов"),
            ("yes", "Есть рецепты"),
        )

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True)
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()


class UserHasFollowersFilter(admin.SimpleListFilter):
    title = "presence of followers"
    parameter_name = "has_followers"

    def lookups(self, request, model_admin):
        return (
            ("no", "Нет подписчиков"),
            ("yes", "Есть подписчики"),
        )

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(authors__isnull=True)
        if self.value() == "yes":
            return queryset.filter(authors__isnull=False).distinct()


class UserHasSubscriptionsFilter(admin.SimpleListFilter):
    title = "presence of subscriptions"
    parameter_name = "has_subscriptions"

    def lookups(self, request, model_admin):
        return (
            ("no", "Нет подписок"),
            ("yes", "Есть подписки"),
        )

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(followers__isnull=True)
        if self.value() == "yes":
            return queryset.filter(followers__isnull=False).distinct()


@admin.register(UserModel)
class UserAdminClass(UserAdmin):
    """Класс админки пользователя"""

    list_display = (
        "id",
        "username",
        "get_full_name",
        "get_avatar",
        "get_recipes_count",
        "email",
        "first_name",
        "surname",
        "get_number_of_following",
        "get_number_of_followers",
    )
    list_filter = (UserHasRecipesFilter, UserHasFollowersFilter, UserHasSubscriptionsFilter, "is_active", "is_staff",
                   "is_superuser")
    search_fields = ("username", "email", "first_name", "surname")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "User info",
            {"fields": ("username", "first_name", "surname", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "surname",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description="FIO")
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.surname}"

    @admin.display(description="avatar")
    @mark_safe
    def get_avatar(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="50" height="50" />'
        return ""

    @admin.display(description="Recipes")
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description="Followers")
    def get_number_of_followers(self, user_obj):
        return user_obj.authors.count()

    @admin.display(description="Subscriptions")
    def get_number_of_following(self, user_obj):
        return user_obj.followers.count()


@admin.register(SubscriptionModel)
class SubscriptionAdminClass(admin.ModelAdmin):
    """Класс подписки админка"""

    search_fields = ("user_from__username", "user_to__username")
    list_filter = ("user_from", "user_to")
    list_display = ("id", "user_from", "user_to")
