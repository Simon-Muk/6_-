from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        # Модератор не может создавать продукты
        if request.method == 'POST':
            return False

        return request.user.is_staff

    def has_object_permission(self, request, view, obj):

        return request.user.is_staff