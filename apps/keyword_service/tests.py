from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import CustomUser
from apps.keyword_service.models import Keyword
from apps.project.models import Project


class KeywordViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='userpass123'
        )
        self.project = Project.objects.create(
            owner=self.regular_user, description='Test Description', name='Test Project Name',
            service_url="https://example.com"
        )
        self.keyword = Keyword.objects.create(
            project=self.project,
            keyword='test',
            root_keyword='Test Root Keyword',
        )
        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.admin_client.login(username='admin', password='adminpass123')
        self.user_client.login(username='user', password='userpass123')

        # Generate JWT tokens for admin and regular user
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def test_admin_create_keyword(self):
        data = {
            'project_id': self.project.id,
            'user_id': self.regular_user.id,
            'keyword': 'newkeyword',
            'root_keyword': 'newrootkeyword'
        }
        response = self.admin_client.post(
            reverse('admin-keyword-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Keyword.objects.count(), 2)
        self.assertEqual(response.data['keyword'], 'newkeyword')
        self.assertEqual(response.data['root_keyword'], 'newrootkeyword')

    def test_admin_create_keyword_invalid(self):
        data = {
            'project_id': self.project.id,
            'user_id': self.regular_user.id,
            'keyword': '',  # Invalid empty keyword
            'status': 'pending'
        }
        response = self.admin_client.post(
            reverse('admin-keyword-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieve_keyword(self):
        response = self.admin_client.get(
            reverse('admin-keyword-detail', kwargs={'id': self.keyword.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.keyword.id)

    def test_admin_update_keyword(self):
        data = {
            'project_id': self.project.id,
            'user_id': self.regular_user.id,
            'keyword': 'updatedkeyword',
            'root_keyword': 'new root keyword'
        }
        response = self.admin_client.put(
            reverse('admin-keyword-detail', kwargs={'id': self.keyword.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.keyword.refresh_from_db()
        self.assertEqual(self.keyword.keyword, 'updatedkeyword')

    def test_admin_partial_update_keyword(self):
        data = {'root_keyword': 'newrootkeyword'}
        response = self.admin_client.patch(
            reverse('admin-keyword-detail', kwargs={'id': self.keyword.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.keyword.refresh_from_db()
        self.assertEqual(self.keyword.root_keyword, 'newrootkeyword')

    def test_admin_delete_keyword(self):
        response = self.admin_client.delete(
            reverse('admin-keyword-detail', kwargs={'id': self.keyword.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Keyword.objects.count(), 0)

    def test_admin_list_keywords(self):
        response = self.admin_client.get(reverse('admin-keyword-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_create_keyword(self):
        data = {'project_id': self.project.id, 'keyword': 'userkeyword', 'root_keyword': 'user root keyword'}
        response = self.user_client.post(
            reverse('keyword-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_user_retrieve_own_keyword(self):
        response = self.user_client.get(
            reverse('keyword-detail', kwargs={'id': self.keyword.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.keyword.id)

    def test_user_retrieve_other_keyword(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )

        project = Project.objects.create(

            owner=other_user, description='Test Description', name='Test Project Name',
            service_url="https://example.com"
        )

        other_keyword = Keyword.objects.create(
            project=project, keyword='otherkeyword', root_keyword='other Test Root Keyword'
        )
        response = self.user_client.get(
            reverse('keyword-detail', kwargs={'id': other_keyword.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_own_keyword(self):
        data = {'project_id': self.project.id, 'keyword': 'updateduserkeyword', 'root_keyword': 'new test keyword'}
        response = self.user_client.put(
            reverse('keyword-detail', kwargs={'id': self.keyword.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_partial_update_own_keyword(self):
        data = {'keyword': 'partiallyupdatedkeyword'}
        response = self.user_client.patch(
            reverse('keyword-detail', kwargs={'id': self.keyword.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_delete_own_keyword(self):
        response = self.user_client.delete(
            reverse('keyword-detail', kwargs={'id': self.keyword.id})
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_list_own_keywords(self):
        response = self.user_client.get(reverse('keyword-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_access(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse('keyword-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)