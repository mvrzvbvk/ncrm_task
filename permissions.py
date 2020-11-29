from rest_framework.permissions import BasePermission

from user.models import User


class IsManagerUser(BasePermission):
    def has_permission(self, request, view):
        user_type = getattr(request.user, "user_type")
        return user_type == User.USER_MANAGER
