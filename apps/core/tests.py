from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from apps.core.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

class CoreViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='userpass123'
        )
        self.admin_client = APIClient()
        self.user_client = APIClient()

        # Generate JWT tokens for admin and regular user
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def test_admin_create_user(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'is_active': True
        }
        response = self.admin_client.post(
            reverse('admin-user-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 3)
        self.assertEqual(response.data['username'], 'newuser')

    def test_admin_create_user_invalid_email(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'newpass123'
        }
        response = self.admin_client.post(
            reverse('admin-user-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieve_user(self):
        response = self.admin_client.get(
            reverse('admin-user-detail', kwargs={'id': self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.regular_user.id)

    def test_admin_update_user(self):
        data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'is_active': True
        }
        response = self.admin_client.put(
            reverse('admin-user-detail', kwargs={'id': self.regular_user.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, 'updateduser')

    def test_admin_partial_update_user(self):
        data = {'email': 'partiallyupdated@example.com'}
        response = self.admin_client.patch(
            reverse('admin-user-detail', kwargs={'id': self.regular_user.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, 'partiallyupdated@example.com')

    def test_admin_delete_user(self):
        response = self.admin_client.delete(
            reverse('admin-user-detail', kwargs={'id': self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_admin_list_users(self):
        response = self.admin_client.get(reverse('admin-user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_retrieve_own_profile(self):
        response = self.user_client.get(
            reverse('user-detail', kwargs={'id': self.regular_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.regular_user.id)

    def test_user_retrieve_other_profile(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )
        response = self.user_client.get(
            reverse('user-detail', kwargs={'id': other_user.id})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_own_profile(self):
        data = {'email': 'newemail@example.com', 'username': self.regular_user.username}
        response = self.user_client.put(
            reverse('user-detail', kwargs={'id': self.regular_user.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, 'newemail@example.com')

    def test_user_partial_update_own_profile(self):
        data = {'email': 'partialnewemail@example.com'}
        response = self.user_client.patch(
            reverse('user-detail', kwargs={'id': self.regular_user.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, 'partialnewemail@example.com')

