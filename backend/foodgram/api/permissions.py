from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrIsAuthor(BasePermission):
    def has_permission(self, request, view):
        # Разрешаем доступ для безопасных методов (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # Для остальных проверяем, что пользователь аутентифицирован
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Безопасные методы разрешены для всех
        if request.method in SAFE_METHODS:
            return True
        # Для изменения объекта — только автор
        return obj.author == request.user
