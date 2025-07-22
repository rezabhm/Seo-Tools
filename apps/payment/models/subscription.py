from datetime import timedelta
from typing import List
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from apps.core.models import CustomUser, BaseModel
from apps.payment.config import expire_time

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class SubscriptionPlan(BaseModel):
    """
    SubscriptionPlan model representing different subscription tiers with associated features and limits.
    """
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Price"),
        help_text=_("Subscription price in USD"),
    )
    keyword_limit = models.PositiveIntegerField(
        verbose_name=_("Keyword Limit"),
        help_text=_("Maximum number of keywords allowed in this plan"),
    )
    is_labeling_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Labeling Enabled"),
        help_text=_("Whether labeling feature is enabled for this plan"),
    )
    is_chatgpt_enabled = models.BooleanField(
        default=False,
        verbose_name=_("ChatGPT Enabled"),
        help_text=_("Whether ChatGPT integration is enabled for this plan"),
    )
    is_free_plan = models.BooleanField(
        default=False,
        verbose_name=_("Free Plan"),
        help_text=_("Indicates if this is a free subscription plan"),
    )

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")
        ordering = ['price']
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['is_free_plan']),
        ]

    def __str__(self) -> str:
        """
        String representation of the SubscriptionPlan instance.
        """
        return f"{self.price} USD Plan{' (Free)' if self.is_free_plan else ''}"

    def clean(self) -> None:
        """
        Custom validation for SubscriptionPlan fields.
        """
        if self.price < 0:
            raise ValidationError(_("Price cannot be negative"))
        if self.keyword_limit < 0:
            raise ValidationError(_("Keyword limit cannot be negative"))


class PlanFeature(BaseModel):
    """
    PlanFeature model representing individual features of a subscription plan.
    """
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Detailed description of the feature"),
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name=_("Subscription Plan"),
        help_text=_("Associated subscription plan for this feature"),
    )

    class Meta:
        verbose_name = _("Plan Feature")
        verbose_name_plural = _("Plan Features")
        ordering = ['description']
        indexes = [
            models.Index(fields=['subscription_plan']),
        ]

    def __str__(self) -> str:
        """
        String representation of the PlanFeature instance.
        """
        return f"Feature: {self.description[:50]}..."

    def clean(self) -> None:
        """
        Custom validation for PlanFeature fields.
        """
        if not self.description.strip():
            raise ValidationError(_("Feature description cannot be empty"))


class UserSubscription(BaseModel):
    """
    UserSubscription model tracking user subscriptions with usage metrics.
    """

    expire_time = models.DateTimeField(
        default=lambda: timezone.now() + timedelta(days=expire_time),
        verbose_name=_("Expiration Time"),
        help_text=_("Timestamp when the subscription expires"),
    )
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_("Subscription Plan"),
        help_text=_("Associated subscription plan"),
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_("User"),
        help_text=_("User associated with this subscription"),
    )
    keywords_extracted = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Keywords Extracted"),
        help_text=_("Number of keywords extracted under this subscription"),
    )
    keywords_extracted_percent = models.FloatField(
        default=0.0,
        verbose_name=_("Keywords Extracted Percentage"),
        help_text=_("Percentage of keyword limit used"),
    )

    class Meta:
        verbose_name = _("User Subscription")
        verbose_name_plural = _("User Subscriptions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['subscription_plan']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription_plan', 'created_at'],
                name='unique_user_subscription'
            ),
        ]

    def __str__(self) -> str:
        """
        String representation of the UserSubscription instance.
        """
        return f"{self.user.username} - {self.subscription_plan} ({self.created_at})"

    def clean(self) -> None:
        """
        Custom validation for UserSubscription fields.
        """
        if self.expire_time <= self.created_at:
            raise ValidationError(_("Expiration time must be after purchase time"))
        if self.keywords_extracted < 0:
            raise ValidationError(_("Keywords extracted cannot be negative"))
        if self.keywords_extracted_percent < 0 or self.keywords_extracted_percent > 100:
            raise ValidationError(_("Keywords extracted percentage must be between 0 and 100"))

    def is_active(self) -> bool:
        """
        Check if the subscription is currently active.
        """
        return self.created_at <= timezone.now() <= self.expire_time

    @classmethod
    def get_active_subscriptions(cls, user: CustomUser) -> List['UserSubscription']:
        """
        Retrieve all active subscriptions for a given user.
        """
        try:
            return list(
                cls.objects.filter(
                    user=user,
                    buy_time__lte=timezone.now(),
                    expire_time__gte=timezone.now()
                )
            )
        except Exception as e:
            logger.error(f"Error retrieving active subscriptions for user {user.username}: {str(e)}")
            return []

    def update_keyword_usage(self, keywords_used: int) -> bool:
        """
        Update keyword usage and percentage for the subscription.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                self.keywords_extracted += keywords_used
                max_keywords = self.subscription_plan.keyword_limit
                self.keywords_extracted_percent = (
                    (self.keywords_extracted / max_keywords) * 100
                    if max_keywords > 0 else 0.0
                )
                self.save()
                logger.info(f"Updated keyword usage for subscription {self.id}")
                return True
        except Exception as e:
            logger.error(f"Error updating keyword usage for subscription {self.id}: {str(e)}")
            return False