from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from .models import Role, UserRole, BusinessElement, AccessRolesRule


class BaseRolesTestCase(APITestCase):

    def setUp(self):
        self.admin_role   = Role.objects.create(name='admin',   description='Администратор')
        self.manager_role = Role.objects.create(name='manager', description='Менеджер')
        self.user_role    = Role.objects.create(name='user',    description='Пользователь')

        self.products_el = BusinessElement.objects.create(name='products')
        self.orders_el   = BusinessElement.objects.create(name='orders')

        self.admin = User.objects.create_user(
            email='admin@test.com', password='pass123',
            first_name='Admin', last_name='User'
        )
        self.manager = User.objects.create_user(
            email='manager@test.com', password='pass123',
            first_name='Manager', last_name='User'
        )
        self.regular = User.objects.create_user(
            email='user@test.com', password='pass123',
            first_name='Regular', last_name='User'
        )

        UserRole.objects.create(user=self.admin,   role=self.admin_role)
        UserRole.objects.create(user=self.manager, role=self.manager_role)
        UserRole.objects.create(user=self.regular, role=self.user_role)

        AccessRolesRule.objects.create(
            role=self.admin_role, element=self.products_el,
            read_permission=True, read_all_permission=True,
            create_permission=True, update_permission=True,
            update_all_permission=True, delete_permission=True,
            delete_all_permission=True,
        )
        AccessRolesRule.objects.create(
            role=self.manager_role, element=self.products_el,
            read_permission=True, read_all_permission=True,
            create_permission=True,
        )
        AccessRolesRule.objects.create(
            role=self.user_role, element=self.products_el,
            read_permission=True,
        )

    def auth(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')



class RoleManagementTests(BaseRolesTestCase):

    def test_admin_can_list_roles(self):
        self.auth(self.admin)
        response = self.client.get(reverse('roles:role-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3) 

    def test_non_admin_cannot_list_roles(self):
        self.auth(self.manager)
        response = self.client.get(reverse('roles:role-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_roles(self):
        response = self.client.get(reverse('roles:role-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_role(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:role-list'), {
            'name': 'superadmin',
            'description': 'Супер администратор',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name='superadmin').exists())

    def test_cannot_create_duplicate_role(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:role-list'), {
            'name': 'admin',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



class AssignRoleTests(BaseRolesTestCase):

    def test_admin_can_assign_role(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:assign'), {
            'user_id': str(self.regular.id),
            'role_id': self.manager_role.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserRole.objects.filter(
            user=self.regular, role=self.manager_role
        ).exists())

    def test_assign_duplicate_role(self):
        self.auth(self.admin)
        self.client.post(reverse('roles:assign'), {
            'user_id': str(self.regular.id),
            'role_id': self.user_role.id,
        }, format='json')
        response = self.client.post(reverse('roles:assign'), {
            'user_id': str(self.regular.id),
            'role_id': self.user_role.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_assign_role(self):
        self.auth(self.manager)
        response = self.client.post(reverse('roles:assign'), {
            'user_id': str(self.regular.id),
            'role_id': self.admin_role.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_revoke_role(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:revoke'), {
            'user_id': str(self.regular.id),
            'role_id': self.user_role.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserRole.objects.filter(
            user=self.regular, role=self.user_role
        ).exists())

    def test_revoke_nonexistent_role(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:revoke'), {
            'user_id': str(self.regular.id),
            'role_id': self.admin_role.id,  
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class AccessRuleTests(BaseRolesTestCase):

    def test_admin_can_list_rules(self):
        self.auth(self.admin)
        response = self.client.get(reverse('roles:rule-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_rules_by_role(self):
        self.auth(self.admin)
        response = self.client.get(
            reverse('roles:rule-list') + f'?role_id={self.admin_role.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_create_rule(self):
        shops_el = BusinessElement.objects.create(name='shops')
        self.auth(self.admin)
        response = self.client.post(reverse('roles:rule-list'), {
            'role': self.user_role.id,
            'element': shops_el.id,
            'read_permission': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_duplicate_rule(self):
        self.auth(self.admin)
        response = self.client.post(reverse('roles:rule-list'), {
            'role': self.admin_role.id,
            'element': self.products_el.id,
            'read_permission': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_update_rule(self):
        rule = AccessRolesRule.objects.get(role=self.user_role, element=self.products_el)
        self.auth(self.admin)
        response = self.client.patch(
            reverse('roles:rule-detail', kwargs={'pk': rule.pk}),
            {'create_permission': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rule.refresh_from_db()
        self.assertTrue(rule.create_permission)



class MyRolesTests(BaseRolesTestCase):

    def test_get_my_roles(self):
        self.auth(self.manager)
        response = self.client.get(reverse('roles:my-roles'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('manager', response.data)

    def test_unauthenticated_cannot_get_roles(self):
        response = self.client.get(reverse('roles:my-roles'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class ResourcePermissionTests(BaseRolesTestCase):

    def test_admin_can_read_all_products(self):
        self.auth(self.admin)
        response = self.client.get(reverse('resources:products'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_manager_can_read_all_products(self):
        self.auth(self.manager)
        response = self.client.get(reverse('resources:products'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_user_reads_limited_products(self):
        self.auth(self.regular)
        response = self.client.get(reverse('resources:products'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_user_cannot_access_orders_without_permission(self):
        self.auth(self.regular)
        response = self.client.get(reverse('resources:orders'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_products(self):
        response = self.client.get(reverse('resources:products'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_product(self):
        self.auth(self.admin)
        response = self.client.post(reverse('resources:products'), {
            'name': 'Новый продукт', 'price': 5000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_product(self):
        self.auth(self.regular)
        response = self.client.post(reverse('resources:products'), {
            'name': 'Новый продукт',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_permissions_returns_correct_structure(self):
        self.auth(self.manager)
        response = self.client.get(reverse('resources:my-permissions'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertTrue(response.data['products']['read_all'])
        self.assertTrue(response.data['products']['create'])
        self.assertFalse(response.data['products']['delete'])