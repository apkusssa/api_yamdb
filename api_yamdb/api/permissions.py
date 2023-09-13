from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Пользователи с ролью 'admin' имеют доступ к изменению ресурсов,
    в противном случае только чтение (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )


class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """
    Хозяин страницы админ или модератор могут редактировать страницу.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdminOrSuperuser(permissions.BasePermission):
    """
    Админ и суперюзер имеют доступ к ресурсам.
    """
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
