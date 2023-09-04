from rest_framework import permissions
from reviews.models import ADMIN


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.role == ADMIN)
        )