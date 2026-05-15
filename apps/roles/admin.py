from django.contrib import admin
from .models import Role, UserRole, BusinessElement, AccessRolesRule


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_at']
    list_filter = ['role']
    search_fields = ['user__email']


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


@admin.register(AccessRolesRule)
class AccessRolesRuleAdmin(admin.ModelAdmin):
    list_display = [
        'role', 'element',
        'read_permission', 'read_all_permission',
        'create_permission', 'update_permission',
        'delete_permission',
    ]
    list_filter = ['role', 'element']