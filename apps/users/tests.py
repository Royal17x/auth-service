from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class BaseTestCase(APITestCase):

    def create_user(self, email='test@example.com', password='testpass123',
                    first_name='Иван', last_name='Петров', is_active=True):
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = is_active
        user.save()
        return user

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    def auth_client(self, user):
        tokens = self.get_tokens(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens


class RegisterTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('users:register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'first_name': 'Иван',
            'last_name': 'Петров',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

        self.assertNotIn('password', response.data['user'])

    def test_register_email_lowercase(self):
        data = {**self.valid_data, 'email': 'UPPERCASE@EXAMPLE.COM'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'uppercase@example.com')

    def test_register_duplicate_email(self):
        self.create_user(email='newuser@example.com')
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_passwords_mismatch(self):
        data = {**self.valid_data, 'password_confirm': 'different123'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_register_password_too_short(self):
        data = {**self.valid_data, 'password': '123', 'password_confirm': '123'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_missing_required_fields(self):
        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_register_invalid_email_format(self):
        data = {**self.valid_data, 'email': 'not-an-email'}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class LoginTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('users:login')
        self.user = self.create_user(email='user@example.com', password='testpass123')

    def test_login_success(self):
        response = self.client.post(self.url, {
            'email': 'user@example.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)

    def test_login_wrong_password(self):
        response = self.client.post(self.url, {
            'email': 'user@example.com',
            'password': 'wrongpassword',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_email(self):
        response = self.client.post(self.url, {
            'email': 'nobody@example.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        inactive_user = self.create_user(
            email='inactive@example.com',
            password='testpass123',
            is_active=False,
        )
        response = self.client.post(self.url, {
            'email': 'inactive@example.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_case_insensitive_email(self):
        response = self.client.post(self.url, {
            'email': 'USER@EXAMPLE.COM',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_missing_fields(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('users:logout')
        self.user = self.create_user()
        self.tokens = self.auth_client(self.user)

    def test_logout_success(self):
        response = self.client.post(self.url, {
            'refresh': self.tokens['refresh'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_token(self):
        self.client.credentials()  
        response = self.client.post(self.url, {
            'refresh': self.tokens['refresh'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_refresh(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_invalidates_refresh_token(self):
        self.client.post(self.url, {'refresh': self.tokens['refresh']}, format='json')

        refresh_url = reverse('users:token-refresh')
        response = self.client.post(refresh_url, {
            'refresh': self.tokens['refresh'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('users:profile')
        self.user = self.create_user(
            email='profile@example.com',
            first_name='Иван',
            last_name='Петров',
        )
        self.auth_client(self.user)

    def test_get_profile_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')
        self.assertEqual(response.data['first_name'], 'Иван')
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        self.assertNotIn('password', response.data)

    def test_get_profile_unauthorized(self):
        self.client.credentials()  
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_patch_first_name_only(self):
        response = self.client.patch(self.url, {
            'first_name': 'Алексей',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Алексей')
        self.assertEqual(response.data['last_name'], 'Петров')

    def test_patch_multiple_fields(self):
        response = self.client.patch(self.url, {
            'first_name': 'Алексей',
            'last_name': 'Сидоров',
            'patronymic': 'Иванович',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Алексей')
        self.assertEqual(response.data['last_name'], 'Сидоров')
        self.assertEqual(response.data['patronymic'], 'Иванович')

    def test_patch_empty_body(self):
        response = self.client.patch(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Иван')

    def test_patch_empty_first_name(self):
        response = self.client.patch(self.url, {
            'first_name': '',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_change_email_via_patch(self):
        response = self.client.patch(self.url, {
            'email': 'newemail@example.com',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')

    def test_delete_deactivates_account(self):
        tokens = self.get_tokens(self.user)
        response = self.client.delete(self.url, {
            'refresh': tokens['refresh'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_delete_prevents_login(self):
        tokens = self.get_tokens(self.user)
        self.client.delete(self.url, {'refresh': tokens['refresh']}, format='json')

        response = self.client.post(reverse('users:login'), {
            'email': 'profile@example.com',
            'password': 'testpass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_soft_delete_keeps_record_in_db(self):
        user_id = self.user.id
        tokens = self.get_tokens(self.user)
        self.client.delete(self.url, {'refresh': tokens['refresh']}, format='json')

        # Запись всё ещё есть в БД
        self.assertTrue(User.objects.filter(id=user_id).exists())


class ChangePasswordTests(BaseTestCase):

    def setUp(self):
        self.url = reverse('users:change-password')
        self.user = self.create_user(password='oldpassword123')
        self.auth_client(self.user)

    def test_change_password_success(self):
        response = self.client.post(self.url, {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

    def test_change_password_wrong_old(self):
        response = self.client.post(self.url, {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'new_password_confirm': 'newpassword456',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        response = self.client.post(self.url, {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'new_password_confirm': 'different789',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_too_short(self):
        response = self.client.post(self.url, {
            'old_password': 'oldpassword123',
            'new_password': '123',
            'new_password_confirm': '123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)