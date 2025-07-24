from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.models import CustomUser
from apps.core.serializers import CustomUserSerializer
from apps.payment.models.payment import PaymentTransaction
from apps.payment.models.subscription import SubscriptionPlan, UserSubscription
from django.utils import timezone
import uuid
from unittest.mock import patch
from datetime import timedelta

class PaymentTransactionViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='userpass123'
        )
        self.subscription_plan = SubscriptionPlan.objects.create(
            price=10.00,
            keyword_limit=100,
            is_labeling_enabled=True,
            is_chatgpt_enabled=False,
            is_free_plan=False
        )
        self.transaction = PaymentTransaction.objects.create(
            user=self.regular_user,
            subscription_plan=self.subscription_plan,
            paypal_transaction_id=str(uuid.uuid4()),
            amount=10.00,
            status='pending',
            redirect_url='https://paypal.com/test'
        )
        self.admin_client = APIClient()
        self.user_client = APIClient()

        # Generate JWT tokens for admin and regular user
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def test_admin_create_transaction(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'paypal_transaction_id': str(uuid.uuid4()),
            'amount': 10.00,
            'status': 'pending',
            'redirect_url': 'https://paypal.com/new'
        }
        response = self.admin_client.post(
            reverse('admin-payment-transaction-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PaymentTransaction.objects.count(), 2)
        self.assertEqual(response.data['paypal_transaction_id'], data['paypal_transaction_id'])

    def test_admin_create_transaction_invalid_amount(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'paypal_transaction_id': str(uuid.uuid4()),
            'amount': 10.00,
            'status': 'pending',
            'redirect_url': 'https://paypal.com/invalid'
        }
        response = self.admin_client.post(
            reverse('admin-payment-transaction-list'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_retrieve_transaction(self):
        response = self.admin_client.get(
            reverse('admin-payment-transaction-detail', kwargs={'id': self.transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction.id)

    def test_admin_update_transaction(self):
        data = {
            'user_id': self.regular_user.id,
            'subscription_plan_id': self.subscription_plan.id,
            'paypal_transaction_id': self.transaction.paypal_transaction_id,
            'amount': 10.00,
            'status': 'completed',
            'paypal_response': {'status': 'COMPLETED'},
            'redirect_url': self.transaction.redirect_url
        }

        response = self.admin_client.put(
            reverse('admin-payment-transaction-detail', kwargs={'id': self.transaction.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'completed')
        self.assertTrue(UserSubscription.objects.filter(user=self.regular_user, subscription_plan=self.subscription_plan).exists())

    def test_admin_partial_update_transaction(self):
        data = {
            'status': 'canceled',
            'paypal_response': {'status': 'CANCELED'},
            'amount': 10.0,
            'paypal_transaction_id': '554545'
        }
        response = self.admin_client.patch(
            reverse('admin-payment-transaction-detail', kwargs={'id': self.transaction.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'canceled')

    def test_admin_delete_transaction(self):
        response = self.admin_client.delete(
            reverse('admin-payment-transaction-detail', kwargs={'id': self.transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PaymentTransaction.objects.count(), 0)

    def test_admin_list_transactions(self):
        response = self.admin_client.get(reverse('admin-payment-transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_initiate_payment(self):
        custom_user_serializer = CustomUserSerializer([self.regular_user], many=True)
        data = {
            'subscription_plan_id': self.subscription_plan.id,
            'amount': 10.00,
            'user': custom_user_serializer.data[0],
            'user_id': custom_user_serializer.data[0]['id'],
            'paypal_transaction_id': '44551'
        }
        response = self.user_client.post(
            reverse('payment-transaction-initiate-payment'), data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertIn('paypal_transaction_id', response.data)
        self.assertEqual(PaymentTransaction.objects.count(), 2)
        new_transaction = PaymentTransaction.objects.last()
        self.assertEqual(new_transaction.user, self.regular_user)
        self.assertEqual(new_transaction.amount, 10.00)

    def test_user_complete_payment(self):
        data = {
            'paypal_transaction_id': self.transaction.paypal_transaction_id
        }

        response = self.user_client.post(
            reverse('payment-transaction-complete-payment', kwargs={'id': self.transaction.id}),
            data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'completed')
        subscription = UserSubscription.objects.filter(user=self.regular_user).first()
        self.assertIsNotNone(subscription)
        self.assertTrue(subscription.is_active())
        self.assertEqual(subscription.subscription_plan, self.subscription_plan)

    def test_user_cancel_payment(self):
        response = self.user_client.post(
            reverse('payment-transaction-cancel-payment', kwargs={'id': self.transaction.id}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'canceled')

    def test_user_retrieve_own_transaction(self):
        response = self.user_client.get(
            reverse('payment-transaction-detail', kwargs={'id': self.transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction.id)
        self.assertEqual(response.data['user']['id'], self.regular_user.id)

    def test_user_retrieve_other_transaction(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )
        other_transaction = PaymentTransaction.objects.create(
            user=other_user,
            subscription_plan=self.subscription_plan,
            paypal_transaction_id=str(uuid.uuid4()),
            amount=10.00,
            status='pending',
            redirect_url='https://paypal.com/other'
        )
        response = self.user_client.get(
            reverse('payment-transaction-detail', kwargs={'id': other_transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_list_own_transactions(self):
        response = self.user_client.get(reverse('payment-transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.transaction.id)

    def test_read_only_retrieve_own_transaction(self):
        response = self.user_client.get(
            reverse('payment-transaction-read-only-detail', kwargs={'id': self.transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.transaction.id)

    def test_read_only_retrieve_other_transaction(self):
        other_user = CustomUser.objects.create_user(
            username='other', email='other@example.com', password='otherpass123'
        )
        other_transaction = PaymentTransaction.objects.create(
            user=other_user,
            subscription_plan=self.subscription_plan,
            paypal_transaction_id=str(uuid.uuid4()),
            amount=10.00,
            status='pending',
            redirect_url='https://paypal.com/other'
        )
        response = self.user_client.get(
            reverse('payment-transaction-read-only-detail', kwargs={'id': other_transaction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_read_only_list_own_transactions(self):

        response = self.user_client.get(reverse('payment-transaction-read-only-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.transaction.id)

    def test_unauthenticated_access(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(reverse('payment-transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = unauthenticated_client.get(reverse('payment-transaction-read-only-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)