from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom user admin class"""

    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "get_number_of_followers",
        "get_number_of_following",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("username", "first_name", "last_name", "avatar")},
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
                    "last_name",
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription admin class"""

    list_display = ("id", "from_user", "to_user")
    list_filter = ("from_user", "to_user")
    search_fields = ("from_user__username", "to_user__username")