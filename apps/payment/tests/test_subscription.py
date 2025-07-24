from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import CustomUser
from apps.payment.models.subscription import SubscriptionPlan, PlanFeature, UserSubscription
from django.utils import timezone
from datetime import timedelta


class SubscriptionViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='userpass123'
        )
        self.subscription_plan = SubscriptionPlan.objects.create(
            price=10.00, keyword_limit=100, is_labeling_enabled=True, is_free_plan=False
        )
        self.plan_feature = PlanFeature.objects.create(
            subscription_plan=self.subscription_plan, description='Feature description'
        )
        self.user_subscription = UserSubscription.objects.create(
            user=self.regular_user,
            subscription_plan=self.subscription_plan,
            expire_time=timezone.now() + timedelta(days=30),
            keywords_extracted=50,
            keywords_extracted_percent=50.0
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

    def test_admin_create_subscription_plan(self):
        data = {
            'price': 20.00,
            'keyword_limit': 200,
            'is_labeling_enabled': False,
            'is_chatgpt_enabled': True,
            'is_free_plan': False
        }
        response = self.admin_client.post(
            reverse('admin-subscription-plan-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubscriptionPlan.objects.count(), 2)
        self.assertAlmostEqual(float(response.data['price']), 20.0, places=2)

    def test_admin_create_subscription_plan_invalid_price(self):
        data = {
            'price': -10.00,
            'keyword_limit': 200,
            'is_labeling_enabled': False,
            'is_chatgpt_enabled': True,
            'is_free_plan': False
        }
        response = self.admin_client.post(
            reverse('admin-subscription-plan-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieve_subscription_plan(self):
        response = self.admin_client.get(
            reverse('admin-subscription-plan-detail', kwargs={'id': self.subscription_plan.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.subscription_plan.id)

    def test_admin_update_subscription_plan(self):
        data = {
            'price': 15.00,
            'keyword_limit': 150,
            'is_labeling_enabled': True,
            'is_chatgpt_enabled': False,
            'is_free_plan': True
        }
        response = self.admin_client.put(
            reverse('admin-subscription-plan-detail', kwargs={'id': self.subscription_plan.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription_plan.refresh_from_db()
        self.assertEqual(self.subscription_plan.price, 15.00)

    def test_admin_partial_update_subscription_plan(self):
        data = {'price': 25.00}
        response = self.admin_client.patch(
            reverse('admin-subscription-plan-detail', kwargs={'id': self.subscription_plan.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.subscription_plan.refresh_from_db()
        self.assertEqual(self.subscription_plan.price, 25.00)

    def test_admin_delete_subscription_plan(self):
        response = self.admin_client.delete(
            reverse('admin-subscription-plan-detail', kwargs={'id': self.subscription_plan.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_list_subscription_plans(self):
        response = self.admin_client.get(reverse('admin-subscription-plan-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_create_plan_feature(self):
        data = {'subscription_plan_id': self.subscription_plan.id, 'description': 'New feature'}
        response = self.admin_client.post(
            reverse('admin-plan-feature-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlanFeature.objects.count(), 2)
        self.assertEqual(response.data['description'], 'New feature')

    def test_admin_create_plan_feature_invalid_description(self):
        data = {'subscription_plan_id': self.subscription_plan.id, 'description': ''}
        response = self.admin_client.post(
            reverse('admin-plan-feature-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieve_plan_feature(self):
        response = self.admin_client.get(
            reverse('admin-plan-feature-detail', kwargs={'id': self.plan_feature.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.plan_feature.id)

    def test_admin_update_plan_feature(self):
        data = {'subscription_plan_id': self.subscription_plan.id, 'description': 'Updated feature'}
        response = self.admin_client.put(
            reverse('admin-plan-feature-detail', kwargs={'id': self.plan_feature.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan_feature.refresh_from_db()
        self.assertEqual(self.plan_feature.description, 'Updated feature')

    def test_admin_partial_update_plan_feature(self):
        data = {'description': 'Partially updated feature'}
        response = self.admin_client.patch(
            reverse('admin-plan-feature-detail', kwargs={'id': self.plan_feature.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.plan_feature.refresh_from_db()
        self.assertEqual(self.plan_feature.description, 'Partially updated feature')

    def test_admin_delete_plan_feature(self):
        response = self.admin_client.delete(
            reverse('admin-plan-feature-detail', kwargs={'id': self.plan_feature.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlanFeature.objects.count(), 0)

    def test_admin_list_plan_features(self):
        response = self.admin_client.get(reverse('admin-plan-feature-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_create_user_subscription(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'expire_time': (timezone.now() + timedelta(days=60)).isoformat(),
            'keywords_extracted': 10,
            'keywords_extracted_percent': 10.0
        }
        response = self.admin_client.post(
            reverse('admin-user-subscription-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserSubscription.objects.count(), 2)

    def test_admin_create_user_subscription_invalid_expire_time(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'expire_time': (timezone.now() - timedelta(days=1)).isoformat(),
            'keywords_extracted': 10,
            'keywords_extracted_percent': 10.0
        }
        response = self.admin_client.post(
            reverse('admin-user-subscription-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieve_user_subscription(self):
        response = self.admin_client.get(
            reverse('admin-user-subscription-detail', kwargs={'id': self.user_subscription.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_subscription.id)

    def test_admin_update_user_subscription(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'expire_time': (timezone.now() + timedelta(days=60)).isoformat(),
            'keywords_extracted': 20,
            'keywords_extracted_percent': 20.0
        }
        response = self.admin_client.put(
            reverse('admin-user-subscription-detail', kwargs={'id': self.user_subscription.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_subscription.refresh_from_db()
        self.assertEqual(self.user_subscription.keywords_extracted, 20)

    def test_admin_partial_update_user_subscription(self):
        data = {'keywords_extracted': 30}
        response = self.admin_client.patch(
            reverse('admin-user-subscription-detail', kwargs={'id': self.user_subscription.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_subscription.refresh_from_db()
        self.assertEqual(self.user_subscription.keywords_extracted, 30)

    def test_admin_delete_user_subscription(self):
        response = self.admin_client.delete(
            reverse('admin-user-subscription-detail', kwargs={'id': self.user_subscription.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_admin_list_user_subscriptions(self):
        response = self.admin_client.get(reverse('admin-user-subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_list_subscription_plans(self):
        response = self.user_client.get(reverse('subscription-plan-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('features', response.data[0])

    def test_user_retrieve_own_subscription(self):
        response = self.user_client.get(
            reverse('user-subscription-detail', kwargs={'id': self.user_subscription.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_subscription.id)
        self.assertTrue(response.data['is_active'])

    def test_user_retrieve_other_subscription(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )
        other_subscription = UserSubscription.objects.create(
            user=other_user,
            subscription_plan=self.subscription_plan,
            expire_time=timezone.now() + timedelta(days=30)
        )
        response = self.user_client.get(
            reverse('user-subscription-detail', kwargs={'id': other_subscription.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_list_own_subscriptions(self):
        response = self.user_client.get(reverse('user-subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_access(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse('subscription-plan-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = unauthenticated_client.get(reverse('user-subscription-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)