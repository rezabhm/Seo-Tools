from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.models import CustomUser, Collaborator
from apps.project.models import Project, Process

class ProjectViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='userpass123'
        )
        self.project = Project.objects.create(
            name="Test Project Name",
            owner=self.regular_user,
            description='Test Description',
            service_url='https://example.com'
        )
        self.process = Process.objects.create(
            project=self.project,
            status='pending',
            extraction_level=1,
            total_count=100,
            completed_count=0
        )
        self.admin_client = APIClient()
        self.user_client = APIClient()

        # Generate JWT tokens for admin and regular user
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def test_admin_create_project(self):
        data = {
            'owner_id': self.regular_user.id,
            'name': 'New Project',
            'description': 'New Description',
            'service_url': 'https://newproject.com'
        }
        response = self.admin_client.post(
            reverse('admin-project-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Project')

    def test_admin_retrieve_project(self):
        response = self.admin_client.get(
            reverse('admin-project-detail', kwargs={'id': self.project.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.project.id)

    def test_admin_update_project(self):
        data = {
            'owner_id': self.regular_user.id,
            'name': 'Updated Project',
            'description': 'Updated Description',
            'service_url': 'https://updatedproject.com'
        }
        response = self.admin_client.put(
            reverse('admin-project-detail', kwargs={'id': self.project.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')

    def test_admin_partial_update_project(self):
        data = {
            'name': 'Partially Updated Project',
            'service_url': 'https://partialproject.com'
        }
        response = self.admin_client.patch(
            reverse('admin-project-detail', kwargs={'id': self.project.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Partially Updated Project')
        self.assertEqual(self.project.service_url, 'https://partialproject.com')

    def test_admin_delete_project(self):
        response = self.admin_client.delete(
            reverse('admin-project-detail', kwargs={'id': self.project.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_admin_list_projects(self):
        response = self.admin_client.get(reverse('admin-project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_create_process(self):
        data = {
            'project_id': self.project.id,
            'status': 'pending',
            'extraction_level': 2,
            'total_count': 200,
            'completed_count': 0
        }
        response = self.admin_client.post(
            reverse('admin-process-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Process.objects.count(), 2)
        self.assertEqual(response.data['extraction_level'], 2)

    def test_admin_retrieve_process(self):
        response = self.admin_client.get(
            reverse('admin-process-detail', kwargs={'id': self.process.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.process.id)

    def test_admin_update_process(self):
        data = {
            'project_id': self.project.id,
            'status': 'finished',
            'extraction_level': 3,
            'total_count': 300,
            'completed_count': 300
        }
        response = self.admin_client.put(
            reverse('admin-process-detail', kwargs={'id': self.process.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.process.refresh_from_db()
        self.assertEqual(self.process.status, 'finished')
        self.assertEqual(self.process.extraction_level, 3)

    def test_admin_partial_update_process(self):
        data = {
            'status': 'finished',
            'completed_count': 50,
            'total_count': 100
        }
        response = self.admin_client.patch(
            reverse('admin-process-detail', kwargs={'id': self.process.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.process.refresh_from_db()
        self.assertEqual(self.process.status, 'finished')
        self.assertEqual(self.process.completed_count, 50)
        self.assertEqual(self.process.total_count, 100)

    def test_admin_delete_process(self):
        response = self.admin_client.delete(
            reverse('admin-process-detail', kwargs={'id': self.process.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Process.objects.count(), 0)

    def test_admin_list_processes(self):
        response = self.admin_client.get(reverse('admin-process-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_create_project(self):
        data = {
            'name': 'User Project',
            'description': 'User Description',
            'service_url': 'https://userproject.com'
        }
        response = self.user_client.post(
            reverse('project-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data['owner']['id'], self.regular_user.id)

    def test_user_retrieve_own_project(self):
        response = self.user_client.get(
            reverse('project-detail', kwargs={'id': self.project.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.project.id)

    def test_user_retrieve_other_project(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )
        other_project = Project.objects.create(
            name="Other Project",
            owner=other_user,
            description='Other Description',
            service_url='https://otherproject.com'
        )
        collaborator = Collaborator.objects.create(
            invitation_sender=self.regular_user,
            invitation_receiver=other_user,
            status='ACCEPT'
        )
        self.project.collaborators.add(collaborator)
        response = self.user_client.get(
            reverse('project-detail', kwargs={'id': other_project.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_list_own_projects(self):
        response = self.user_client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_create_process(self):
        data = {
            'project_id': self.project.id,
            'status': 'pending',
            'extraction_level': 1,
            'total_count': 100,
            'completed_count': 0
        }
        response = self.user_client.post(
            reverse('admin-process-list'), data, format='json'  # Changed to admin-process-list
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_retrieve_own_process(self):
        collaborator = Collaborator.objects.create(
            invitation_sender=self.regular_user,
            invitation_receiver=self.admin_user,
            status='ACCEPT'
        )
        self.project.collaborators.add(collaborator)
        response = self.user_client.get(
            reverse('process-detail', kwargs={'id': self.process.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.process.id)

    def test_user_list_own_processes(self):
        response = self.user_client.get(reverse('process-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_access(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse('project-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = unauthenticated_client.get(reverse('process-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)