from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from models import UserModel, SubscriptionModel


@admin.register(UserModel)
class UserAdminClass(UserAdmin):
    """Класс админки пользователя"""

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "surname",
        "get_number_of_following",
        "get_number_of_followers",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "surname")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
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
        ("Important dates", {"fields": ("last_login", "date_joined")}),
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

    @admin.display(description="followers")
    def get_number_of_followers(self, obj):
        return obj.followers.count()

    @admin.display(description="following")
    def get_number_of_following(self, obj):
        return obj.following.count()


@admin.register(SubscriptionModel)
class SubscriptionAdminClass(admin.ModelAdmin):
    """Класс подписки админка"""

    search_fields = ("user_from__username", "user_to__username")
    list_filter = ("user_from", "user_to")
    list_display = ("id", "user_from", "user_to")
