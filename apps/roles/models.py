from django.db import models
from apps.users.models import User


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,   
        related_name='user_roles'   
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')  

    def __str__(self):
        return f'{self.user.email} → {self.role.name}'


class BusinessElement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'business_elements'

    def __str__(self):
        return self.name


class AccessRolesRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='access_rules')

    read_permission       = models.BooleanField(default=False)
    read_all_permission   = models.BooleanField(default=False)
    create_permission     = models.BooleanField(default=False)
    update_permission     = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission     = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        db_table = 'access_roles_rules'
        unique_together = ('role', 'element')  

    def __str__(self):
        return f'{self.role.name} → {self.element.name}'