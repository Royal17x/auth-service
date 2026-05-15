from rest_framework import serializers
from .models import Role, UserRole, BusinessElement, AccessRolesRule
from apps.users.models import User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'description']


class AccessRolesRuleSerializer(serializers.ModelSerializer):
    role_name    = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)

    class Meta:
        model = AccessRolesRule
        fields = [
            'id',
            'role', 'role_name',
            'element', 'element_name',
            'read_permission',
            'read_all_permission',
            'create_permission',
            'update_permission',
            'update_all_permission',
            'delete_permission',
            'delete_all_permission',
        ]

    def validate(self, data):
        role    = data.get('role', getattr(self.instance, 'role', None))
        element = data.get('element', getattr(self.instance, 'element', None))

        qs = AccessRolesRule.objects.filter(role=role, element=element)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Правило для этой пары роль+ресурс уже существует.'
            )
        return data


class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError('Пользователь не найден или неактивен.')
        return value

    def validate_role_id(self, value):
        if not Role.objects.filter(id=value).exists():
            raise serializers.ValidationError('Роль не найдена.')
        return value


class RevokeRoleSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    role_id = serializers.IntegerField()


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user_email', 'role', 'assigned_at']