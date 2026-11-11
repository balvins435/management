
from rest_framework.permissions import BasePermission

# Admin access
class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )

# Resource managers access
class IsResourceManager(BasePermission):
 
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "RESOURCE_MANAGER"
        )

# Admins and Resource managers access
class IsAdminOrResourceManager(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in [
                "ADMIN",
                "RESOURCE_MANAGER"
            ]
        )


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "EMPLOYEE"
