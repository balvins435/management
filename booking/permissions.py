from rest_framework.permissions import BasePermission


class BookingPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action == 'create':
            return request.user.role in ['EMPLOYEE', 'ADMIN']
        if view.action in ['approve', 'reject', 'complete']:
            return request.user.role in ['ADMIN', 'RESOURCE_MANAGER']
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['ADMIN', 'RESOURCE_MANAGER']:
            return True
        return obj.user_id == request.user.id
