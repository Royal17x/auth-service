from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.roles.models import Role, UserRole, BusinessElement, AccessRolesRule


class Command(BaseCommand):
    help = 'Заполняет БД начальными ролями, правами и тестовыми пользователями'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создаём роли...')
        admin_role,   _ = Role.objects.get_or_create(name='admin',   defaults={'description': 'Полный доступ'})
        manager_role, _ = Role.objects.get_or_create(name='manager', defaults={'description': 'Управление продуктами и заказами'})
        user_role,    _ = Role.objects.get_or_create(name='user',    defaults={'description': 'Базовый пользователь'})
        guest_role,   _ = Role.objects.get_or_create(name='guest',   defaults={'description': 'Только чтение'})

        self.stdout.write('Создаём бизнес-элементы...')
        elements = {}
        for name in ['products', 'orders', 'shops', 'users', 'access_rules']:
            el, _ = BusinessElement.objects.get_or_create(name=name)
            elements[name] = el

        self.stdout.write('Настраиваем права...')

        for el in elements.values():
            AccessRolesRule.objects.update_or_create(
                role=admin_role, element=el,
                defaults={
                    'read_permission': True, 'read_all_permission': True,
                    'create_permission': True, 'update_permission': True,
                    'update_all_permission': True, 'delete_permission': True,
                    'delete_all_permission': True,
                }
            )

        for el_name in ['products', 'orders']:
            AccessRolesRule.objects.update_or_create(
                role=manager_role, element=elements[el_name],
                defaults={
                    'read_permission': True, 'read_all_permission': True,
                    'create_permission': True, 'update_permission': True,
                    'update_all_permission': True,
                    'delete_permission': False, 'delete_all_permission': False,
                }
            )
        AccessRolesRule.objects.update_or_create(
            role=manager_role, element=elements['shops'],
            defaults={'read_permission': True, 'read_all_permission': True}
        )

        AccessRolesRule.objects.update_or_create(
            role=user_role, element=elements['products'],
            defaults={'read_permission': True}
        )
        AccessRolesRule.objects.update_or_create(
            role=user_role, element=elements['orders'],
            defaults={'read_permission': True}
        )

        AccessRolesRule.objects.update_or_create(
            role=guest_role, element=elements['products'],
            defaults={'read_permission': True}
        )

        self.stdout.write('Создаём тестовых пользователей...')

        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={'first_name': 'Admin', 'last_name': 'User', 'is_staff': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        UserRole.objects.get_or_create(user=admin_user, role=admin_role)

        manager_user, created = User.objects.get_or_create(
            email='manager@example.com',
            defaults={'first_name': 'Manager', 'last_name': 'User'}
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
        UserRole.objects.get_or_create(user=manager_user, role=manager_role)

        regular_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={'first_name': 'Regular', 'last_name': 'User'}
        )
        if created:
            regular_user.set_password('user123')
            regular_user.save()
        UserRole.objects.get_or_create(user=regular_user, role=user_role)

        # Гость
        guest_user, created = User.objects.get_or_create(
            email='guest@example.com',
            defaults={'first_name': 'Guest', 'last_name': 'User'}
        )
        if created:
            guest_user.set_password('guest123')
            guest_user.save()
        UserRole.objects.get_or_create(user=guest_user, role=guest_role)

        self.stdout.write(self.style.SUCCESS(
            '\nГотово. Тестовые пользователи:\n'
            '  admin@example.com    / admin123   (роль: admin)\n'
            '  manager@example.com  / manager123 (роль: manager)\n'
            '  user@example.com     / user123    (роль: user)\n'
            '  guest@example.com    / guest123   (роль: guest)\n'
        ))