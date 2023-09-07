from rest_framework import permissions

USER = "user"
ADMIN = "admin"
MODERATOR = "moderator"


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == ADMIN)
        )


class OwnerModeratorAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == ADMIN
            or request.user.role == MODERATOR
        )


from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user
            or request.user.is_admin
            or request.user.is_superuser)