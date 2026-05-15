from rest_framework.permissions import BasePermission
from .models import UserRole, AccessRolesRule


def get_user_role_ids(user):
    return UserRole.objects.filter(user=user).values_list('role_id', flat=True)


def has_permission(user, element_name: str, permission_type: str) -> bool:
    role_ids = get_user_role_ids(user)
    if not role_ids:
        return False

    field_name = f'{permission_type}_permission'

    return AccessRolesRule.objects.filter(
        role_id__in=role_ids,
        element__name=element_name,
        **{field_name: True}
    ).exists()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name='admin'
        ).exists()


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['admin', 'manager']
        ).exists()