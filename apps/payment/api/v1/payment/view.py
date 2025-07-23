from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.payment.api.v1.payment.utils import create_paypal_payment, capture_paypal_payment
from apps.payment.models.payment import PaymentTransaction
from apps.payment.serializers.payment import PaymentTransactionSerializer
from apps.payment.api.v1.payment.swagger_decorator import (
    admin_create_payment_transaction_swagger,
    admin_retrieve_payment_transaction_swagger,
    admin_update_payment_transaction_swagger,
    admin_partial_update_payment_transaction_swagger,
    admin_destroy_payment_transaction_swagger,
    admin_list_payment_transaction_swagger,
    user_initiate_payment_swagger,
    user_complete_payment_swagger,
    user_cancel_payment_swagger,
    user_retrieve_payment_transaction_swagger,
    user_list_payment_transaction_swagger,
)
import logging

# Configure logging
logger = logging.getLogger(__name__)


@method_decorator(name='create', decorator=admin_create_payment_transaction_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_payment_transaction_swagger)
@method_decorator(name='update', decorator=admin_update_payment_transaction_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_payment_transaction_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_payment_transaction_swagger)
@method_decorator(name='list', decorator=admin_list_payment_transaction_swagger)
class PaymentTransactionAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing PaymentTransaction records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = PaymentTransactionSerializer
    lookup_field = 'id'
    queryset = PaymentTransaction.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['paypal_transaction_id', 'user__username', 'status']


@method_decorator(name='initiate_payment', decorator=user_initiate_payment_swagger)
@method_decorator(name='complete_payment', decorator=user_complete_payment_swagger)
@method_decorator(name='cancel_payment', decorator=user_cancel_payment_swagger)
@method_decorator(name='retrieve', decorator=user_retrieve_payment_transaction_swagger)
@method_decorator(name='list', decorator=user_list_payment_transaction_swagger)
class PaymentTransactionAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Authenticated user API ViewSet for managing own PaymentTransaction records.
    Allows initiating, completing, canceling, and viewing transactions.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to transactions belonging to the authenticated user.
        """
        return PaymentTransaction.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve their own transactions.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(_('You can only access your own transactions.'))
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """
        Create a new payment transaction and return a PayPal redirect URL.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set user to authenticated user
        serializer.validated_data['user'] = self.request.user

        # Generate PayPal transaction ID and redirect URL (replace with actual PayPal API call)
        try:
            paypal_transaction_id, redirect_url = create_paypal_payment(
                amount=serializer.validated_data['amount'],
                subscription_plan_id=serializer.validated_data['subscription_plan'].id,
                return_url=request.build_absolute_uri('/api/payment/v1/complete/'),
                cancel_url=request.build_absolute_uri('/api/payment/v1/cancel/')
            )
            serializer.validated_data['paypal_transaction_id'] = paypal_transaction_id
            serializer.validated_data['redirect_url'] = redirect_url
        except Exception as e:
            logger.error(f"Error initiating PayPal payment: {str(e)}")
            raise ValidationError(_("Failed to initiate PayPal payment"))

        # Create the transaction
        transaction = serializer.save()
        return Response({
            'transaction': serializer.data,
            'redirect_url': redirect_url
        }, status=201)

    @action(detail=True, methods=['post'])
    def complete_payment(self, request, id=None):
        """
        Complete a payment transaction using PayPal response and create a subscription.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(_('You can only complete your own transactions.'))
        if instance.status != 'pending':
            raise ValidationError(_('Only pending transactions can be completed.'))

        # Capture PayPal payment (replace with actual PayPal API call)
        try:
            paypal_response = capture_paypal_payment(instance.paypal_transaction_id)
        except Exception as e:
            logger.error(f"Error capturing PayPal payment for transaction {instance.paypal_transaction_id}: {str(e)}")
            raise ValidationError(_("Failed to complete PayPal payment"))

        # Complete the transaction and create subscription
        serializer = self.get_serializer(instance)
        response_data = serializer.complete_payment_action(instance, paypal_response)
        return Response(response_data)

    @action(detail=True, methods=['post'])
    def cancel_payment(self, request, id=None):
        """
        Cancel a pending payment transaction.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(_('You can only cancel your own transactions.'))
        if instance.status != 'pending':
            raise ValidationError(_('Only pending transactions can be canceled.'))

        if not instance.cancel_payment():
            raise ValidationError(_('Failed to cancel transaction.'))

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@method_decorator(name='retrieve', decorator=user_retrieve_payment_transaction_swagger)
@method_decorator(name='list', decorator=user_list_payment_transaction_swagger)
class PaymentTransactionReadOnlyAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Read-only API ViewSet for authenticated users to view their own PaymentTransaction records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to transactions belonging to the authenticated user.
        """
        return PaymentTransaction.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve their own transactions.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(_('You can only access your own transactions.'))
        return super().retrieve(request, *args, **kwargs)