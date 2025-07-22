from typing import Optional, Dict, Any, List
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from datetime import timedelta
from apps.core.models import CustomUser, BaseModel
from apps.payment.models.subscription import SubscriptionPlan, UserSubscription

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class PaymentTransaction(BaseModel):
    """
    PaymentTransaction model for managing PayPal payment transactions.
    Handles the payment process from initiation to completion, including subscription creation.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('canceled', _('Canceled')),
        ('refunded', _('Refunded')),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_("User"),
        help_text=_("User initiating the payment"),
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_("Subscription Plan"),
        help_text=_("Associated subscription plan for this transaction"),
    )
    paypal_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("PayPal Transaction ID"),
        help_text=_("Unique PayPal transaction identifier"),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Transaction amount in USD"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Status"),
        help_text=_("Current status of the transaction"),
    )
    paypal_response = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        verbose_name=_("PayPal Response"),
        help_text=_("Raw PayPal API response data"),
    )
    redirect_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Redirect URL"),
        help_text=_("URL for PayPal payment redirection"),
    )

    class Meta:
        verbose_name = _("Payment Transaction")
        verbose_name_plural = _("Payment Transactions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paypal_transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'paypal_transaction_id'],
                name='unique_user_paypal_transaction'
            ),
        ]

    def __str__(self) -> str:
        """
        String representation of the PaymentTransaction instance.
        """
        return f"Transaction {self.paypal_transaction_id} ({self.status})"

    def clean(self) -> None:
        """
        Custom validation for PaymentTransaction fields.
        """
        if self.amount <= 0:
            raise ValidationError(_("Transaction amount must be positive"))
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValidationError(_("Invalid transaction status"))
        if self.redirect_url and len(self.redirect_url) > 500:
            raise ValidationError(_("Redirect URL cannot exceed 500 characters"))
        if not self.paypal_transaction_id.strip():
            raise ValidationError(_("PayPal transaction ID cannot be empty"))
        if self.subscription_plan and self.amount != self.subscription_plan.price:
            raise ValidationError(_("Transaction amount must match the subscription plan price"))

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to include validation and logging.
        """
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved PaymentTransaction: {self.paypal_transaction_id} (ID: {self.id})")
        except ValidationError as e:
            logger.error(f"Validation error saving PaymentTransaction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving PaymentTransaction: {str(e)}")
            raise

    def initiate_payment(self, redirect_url: str) -> bool:
        """
        Initiate a PayPal payment by setting the redirect URL and updating status.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status != 'pending':
                    logger.warning(f"Cannot initiate non-pending transaction {self.paypal_transaction_id}")
                    return False
                self.redirect_url = redirect_url
                self.save()
                logger.info(f"Initiated PayPal payment for transaction {self.paypal_transaction_id}")
                return True
        except Exception as e:
            logger.error(f"Error initiating payment for transaction {self.paypal_transaction_id}: {str(e)}")
            return False

    def complete_payment(self, paypal_response: Dict[str, Any]) -> Optional[UserSubscription]:
        """
        Complete the payment, update status, and create a corresponding subscription.
        Returns the created UserSubscription instance or None if failed.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status != 'pending':
                    logger.warning(f"Cannot complete non-pending transaction {self.paypal_transaction_id}")
                    return None

                self.status = 'completed'
                self.paypal_response = paypal_response
                self.save()

                # Calculate subscription duration based on plan (default 30 days)
                duration_days = getattr(self.subscription_plan, 'duration_days', 30)
                subscription = UserSubscription.objects.create(
                    user=self.user,
                    subscription_plan=self.subscription_plan,
                    expire_time=timezone.now() + timedelta(days=duration_days),
                    keywords_extracted=0,
                    keywords_extracted_percent=0.0
                )
                logger.info(f"Created subscription {subscription.id} for transaction {self.paypal_transaction_id}")
                return subscription
        except Exception as e:
            logger.error(f"Error completing payment for transaction {self.paypal_transaction_id}: {str(e)}")
            return None

    def fail_payment(self, paypal_response: Dict[str, Any]) -> bool:
        """
        Mark the transaction as failed and store the PayPal response.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status != 'pending':
                    logger.warning(f"Cannot fail non-pending transaction {self.paypal_transaction_id}")
                    return False
                self.status = 'failed'
                self.paypal_response = paypal_response
                self.save()
                logger.info(f"Marked transaction {self.paypal_transaction_id} as failed")
                return True
        except Exception as e:
            logger.error(f"Error failing transaction {self.paypal_transaction_id}: {str(e)}")
            return False

    def cancel_payment(self) -> bool:
        """
        Cancel the transaction.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status != 'pending':
                    logger.warning(f"Cannot cancel transaction {self.paypal_transaction_id} with status {self.status}")
                    return False
                self.status = 'canceled'
                self.save()
                logger.info(f"Canceled transaction {self.paypal_transaction_id}")
                return True
        except Exception as e:
            logger.error(f"Error canceling transaction {self.paypal_transaction_id}: {str(e)}")
            return False

    def refund_payment(self, paypal_response: Dict[str, Any]) -> bool:
        """
        Mark the transaction as refunded and store the PayPal response.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status != 'completed':
                    logger.warning(f"Cannot refund non-completed transaction {self.paypal_transaction_id}")
                    return False
                self.status = 'refunded'
                self.paypal_response = paypal_response
                self.save()
                logger.info(f"Refunded transaction {self.paypal_transaction_id}")
                return True
        except Exception as e:
            logger.error(f"Error refunding transaction {self.paypal_transaction_id}: {str(e)}")
            return False

    @classmethod
    def get_user_transactions(cls, user: CustomUser) -> List['PaymentTransaction']:
        """
        Retrieve all transactions for a given user.
        """
        try:
            return list(cls.objects.filter(user=user).order_by('-created_at'))
        except Exception as e:
            logger.error(f"Error retrieving transactions for user {user.username}: {str(e)}")
            return []

    @classmethod
    def get_pending_transactions(cls) -> List['PaymentTransaction']:
        """
        Retrieve all pending transactions for monitoring.
        """
        try:
            return list(cls.objects.filter(status='pending'))
        except Exception as e:
            logger.error(f"Error retrieving pending transactions: {str(e)}")
            return []