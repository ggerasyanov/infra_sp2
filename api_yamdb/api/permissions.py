from rest_framework import permissions


class IsSuperuserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_authenticated
                and request.user.is_admin)


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """Класс для контроля допуска пользователей."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                or request.user.is_superuser
                or request.method in permissions.SAFE_METHODS
            )
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin
                 or request.user.is_superuser)
        )
