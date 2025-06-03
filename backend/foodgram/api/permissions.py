from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djoser import permissions


class IsAuthorOrStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff