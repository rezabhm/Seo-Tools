from typing import Dict, Any, Optional
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from apps.core.models import CustomUser
from apps.payment.models.subscription import SubscriptionPlan, UserSubscription
from apps.payment.models.payment import PaymentTransaction
from apps.core.serializers import CustomUserSerializer
from apps.payment.serializers.subscription import SubscriptionPlanSerializer

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the PaymentTransaction model, handling PayPal payment transactions and subscription creation.
    Includes calculated field for subscription remaining days.
    """
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='user',
        write_only=True,
        required=True,
        help_text=_("ID of the user initiating the payment")
    )
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    subscription_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='subscription_plan',
        write_only=True,
        required=True,
        help_text=_("ID of the associated subscription plan")
    )
    subscription_remaining_days = serializers.SerializerMethodField(
        help_text=_("Remaining days for the associated subscription, if any")
    )

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'user', 'user_id', 'subscription_plan', 'subscription_plan_id',
            'paypal_transaction_id', 'amount', 'status', 'paypal_response',
            'redirect_url', 'subscription_remaining_days', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'subscription_plan', 'created_at',
            'updated_at', 'subscription_remaining_days'
        ]

    def get_subscription_remaining_days(self, obj: PaymentTransaction) -> Optional[int]:
        """
        Calculate the remaining days for the associated subscription, if it exists.
        Returns None if no subscription is linked or if the subscription has expired.
        """
        try:
            subscription = UserSubscription.objects.filter(
                user=obj.user,
                subscription_plan=obj.subscription_plan,
                created_at__lte=obj.created_at,
                expire_time__gte=obj.created_at
            ).first()
            if subscription and subscription.expire_time > timezone.now():
                remaining = (subscription.expire_time - timezone.now()).days
                return max(0, remaining)
            return None
        except Exception as e:
            logger.error(f"Error calculating subscription remaining days for transaction {obj.paypal_transaction_id}: {str(e)}")
            return None

    def validate_paypal_transaction_id(self, value: str) -> str:
        """
        Validate the PayPal transaction ID.
        """
        if not value.strip():
            logger.error("PayPal transaction ID provided is empty")
            raise serializers.ValidationError(_("PayPal transaction ID cannot be empty"))
        if PaymentTransaction.objects.filter(paypal_transaction_id=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            logger.error(f"Duplicate PayPal transaction ID: {value}")
            raise serializers.ValidationError(_("PayPal transaction ID must be unique"))
        return value

    def validate_amount(self, value: float) -> float:
        """
        Validate the transaction amount.
        """
        if value <= 0:
            logger.error(f"Invalid transaction amount provided: {value}")
            raise serializers.ValidationError(_("Transaction amount must be positive"))
        return value

    def validate_status(self, value: str) -> str:
        """
        Validate the transaction status.
        """
        if value not in dict(PaymentTransaction.STATUS_CHOICES):
            logger.error(f"Invalid transaction status provided: {value}")
            raise serializers.ValidationError(_("Invalid transaction status"))
        return value

    def validate_redirect_url(self, value: str) -> str:
        """
        Validate the redirect URL.
        """
        if value and len(value) > 500:
            logger.error(f"Redirect URL exceeds 500 characters: {value}")
            raise serializers.ValidationError(_("Redirect URL cannot exceed 500 characters"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the PaymentTransaction instance.
        """
        try:
            if 'subscription_plan' in data and 'amount' in data:
                if data['amount'] != data['subscription_plan'].price:
                    logger.error(f"Transaction amount {data['amount']} does not match subscription plan price {data['subscription_plan'].price}")
                    raise serializers.ValidationError(_("Transaction amount must match the subscription plan price"))

            instance = PaymentTransaction(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in PaymentTransactionSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in PaymentTransactionSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> PaymentTransaction:
        """
        Create a new PaymentTransaction instance with validated data.
        """
        try:
            transaction = PaymentTransaction.objects.create(**validated_data)
            logger.info(f"Created payment transaction: {transaction.paypal_transaction_id} (ID: {transaction.id})")
            return transaction
        except Exception as e:
            logger.error(f"Error creating payment transaction: {str(e)}")
            raise serializers.ValidationError(_("Failed to create payment transaction"))

    def update(self, instance: PaymentTransaction, validated_data: Dict[str, Any]) -> PaymentTransaction:
        """
        Update an existing PaymentTransaction instance with validated data.
        """
        try:
            allowed_fields = ['status', 'paypal_response', 'redirect_url']
            for attr, value in validated_data.items():
                if attr in allowed_fields:
                    setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated payment transaction: {instance.paypal_transaction_id} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating payment transaction {instance.paypal_transaction_id}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update payment transaction"))

    def initiate_payment_action(self, instance: PaymentTransaction, redirect_url: str) -> Dict[str, Any]:
        """
        Custom action to initiate a payment and return the redirect URL.
        Can be used in views for initiating PayPal payments.
        """
        try:
            if instance.initiate_payment(redirect_url):
                instance.refresh_from_db()
                return self.to_representation(instance)
            logger.error(f"Failed to initiate payment for transaction {instance.paypal_transaction_id}")
            raise serializers.ValidationError(_("Failed to initiate payment"))
        except Exception as e:
            logger.error(f"Error in initiate_payment_action for transaction {instance.paypal_transaction_id}: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during payment initiation"))

    def complete_payment_action(self, instance: PaymentTransaction, paypal_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Custom action to complete a payment and create a subscription.
        Returns the updated transaction and created subscription data.
        """
        try:
            subscription = instance.complete_payment(paypal_response)
            instance.refresh_from_db()
            response_data = self.to_representation(instance)
            if subscription:
                from apps.payment.serializers.subscription import UserSubscriptionSerializer
                response_data['subscription'] = UserSubscriptionSerializer(subscription).data
            return response_data
        except Exception as e:
            logger.error(f"Error in complete_payment_action for transaction {instance.paypal_transaction_id}: {str(e)}")
            raise serializers.ValidationError(_("Failed to complete payment"))

    def to_representation(self, instance: PaymentTransaction) -> Dict[str, Any]:
        """
        Customize the representation to include subscription remaining days and exclude write-only fields.
        """
        representation = super().to_representation(instance)
        representation.pop('user_id', None)
        representation.pop('subscription_plan_id', None)
        return representation
