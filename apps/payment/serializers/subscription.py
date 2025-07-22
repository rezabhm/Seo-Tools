from typing import Dict, Any, List, Optional
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from apps.core.models import CustomUser
from apps.payment.models.payment import SubscriptionPlan, UserSubscription
from apps.payment.models.subscription import PlanFeature
from apps.core.serializers import CustomUserSerializer

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubscriptionPlan model, handling subscription tier data and features.
    """
    features = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'price', 'keyword_limit', 'is_labeling_enabled',
            'is_chatgpt_enabled', 'is_free_plan', 'features',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'features']

    def validate_price(self, value: float) -> float:
        """
        Validate the price field.
        """
        if value < 0:
            logger.error(f"Negative price provided: {value}")
            raise serializers.ValidationError(_("Price cannot be negative"))
        return value

    def validate_keyword_limit(self, value: int) -> int:
        """
        Validate the keyword_limit field.
        """
        if value < 0:
            logger.error(f"Negative keyword limit provided: {value}")
            raise serializers.ValidationError(_("Keyword limit cannot be negative"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the SubscriptionPlan instance.
        """
        try:
            instance = SubscriptionPlan(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in SubscriptionPlanSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in SubscriptionPlanSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> SubscriptionPlan:
        """
        Create a new SubscriptionPlan instance with validated data.
        """
        try:
            plan = SubscriptionPlan.objects.create(**validated_data)
            logger.info(f"Created subscription plan: {plan} (ID: {plan.id})")
            return plan
        except Exception as e:
            logger.error(f"Error creating subscription plan: {str(e)}")
            raise serializers.ValidationError(_("Failed to create subscription plan"))

    def update(self, instance: SubscriptionPlan, validated_data: Dict[str, Any]) -> SubscriptionPlan:
        """
        Update an existing SubscriptionPlan instance with validated data.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated subscription plan: {instance} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating subscription plan {instance}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update subscription plan"))

class PlanFeatureSerializer(serializers.ModelSerializer):
    """
    Serializer for the PlanFeature model, handling individual feature data for subscription plans.
    """
    subscription_plan = serializers.StringRelatedField(read_only=True)
    subscription_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='subscription_plan',
        write_only=True,
        required=True,
        help_text=_("ID of the associated subscription plan")
    )

    class Meta:
        model = PlanFeature
        fields = [
            'id', 'description', 'subscription_plan', 'subscription_plan_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscription_plan']

    def validate_description(self, value: str) -> str:
        """
        Validate the description field.
        """
        if not value.strip():
            logger.error("Feature description provided is empty")
            raise serializers.ValidationError(_("Feature description cannot be empty"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the PlanFeature instance.
        """
        try:
            instance = PlanFeature(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in PlanFeatureSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in PlanFeatureSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> PlanFeature:
        """
        Create a new PlanFeature instance with validated data.
        """
        try:
            feature = PlanFeature.objects.create(**validated_data)
            logger.info(f"Created plan feature: {feature} (ID: {feature.id})")
            return feature
        except Exception as e:
            logger.error(f"Error creating plan feature: {str(e)}")
            raise serializers.ValidationError(_("Failed to create plan feature"))

    def update(self, instance: PlanFeature, validated_data: Dict[str, Any]) -> PlanFeature:
        """
        Update an existing PlanFeature instance with validated data.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated plan feature: {instance} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating plan feature {instance}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update plan feature"))

    def to_representation(self, instance: PlanFeature) -> Dict[str, Any]:
        """
        Customize the representation to exclude subscription_plan_id.
        """
        representation = super().to_representation(instance)
        representation.pop('subscription_plan_id', None)
        return representation

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserSubscription model, handling user subscription data with usage metrics.
    Includes calculated field for remaining subscription days.
    """
    user = CustomUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='user',
        write_only=True,
        required=True,
        help_text=_("ID of the user associated with the subscription")
    )
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    subscription_plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all(),
        source='subscription_plan',
        write_only=True,
        required=True,
        help_text=_("ID of the associated subscription plan")
    )
    remaining_days = serializers.SerializerMethodField(
        help_text=_("Remaining days until the subscription expires")
    )
    is_active = serializers.SerializerMethodField(
        help_text=_("Whether the subscription is currently active")
    )

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user', 'user_id', 'subscription_plan', 'subscription_plan_id',
            'expire_time', 'keywords_extracted', 'keywords_extracted_percent',
            'remaining_days', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'subscription_plan', 'created_at', 'updated_at',
            'remaining_days', 'is_active'
        ]

    def get_remaining_days(self, obj: UserSubscription) -> Optional[int]:
        """
        Calculate the remaining days until the subscription expires.
        """
        try:
            if obj.expire_time > timezone.now():
                remaining = (obj.expire_time - timezone.now()).days
                return max(0, remaining)
            return 0
        except Exception as e:
            logger.error(f"Error calculating remaining days for subscription {obj.id}: {str(e)}")
            return 0

    def get_is_active(self, obj: UserSubscription) -> bool:
        """
        Determine if the subscription is currently active.
        """
        try:
            return obj.is_active()
        except Exception as e:
            logger.error(f"Error checking active status for subscription {obj.id}: {str(e)}")
            return False

    def validate_expire_time(self, value: timezone.datetime) -> timezone.datetime:
        """
        Validate the expire_time field.
        """
        if value <= timezone.now():
            logger.error(f"Expiration time is not in the future: {value}")
            raise serializers.ValidationError(_("Expiration time must be in the future"))
        return value

    def validate_keywords_extracted(self, value: int) -> int:
        """
        Validate the keywords_extracted field.
        """
        if value < 0:
            logger.error(f"Negative keywords extracted provided: {value}")
            raise serializers.ValidationError(_("Keywords extracted cannot be negative"))
        return value

    def validate_keywords_extracted_percent(self, value: float) -> float:
        """
        Validate the keywords_extracted_percent field.
        """
        if value < 0 or value > 100:
            logger.error(f"Invalid keywords extracted percentage: {value}")
            raise serializers.ValidationError(_("Keywords extracted percentage must be between 0 and 100"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the UserSubscription instance.
        """
        try:
            instance = UserSubscription(**data)
            instance.clean()
            if 'keywords_extracted' in data and 'subscription_plan' in data:
                max_keywords = data['subscription_plan'].keyword_limit
                if max_keywords > 0 and data['keywords_extracted'] > max_keywords:
                    logger.error(f"Keywords extracted {data['keywords_extracted']} exceeds plan limit {max_keywords}")
                    raise serializers.ValidationError(_("Keywords extracted cannot exceed the plan's keyword limit"))
            return data
        except ValidationError as e:
            logger.error(f"Validation error in UserSubscriptionSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in UserSubscriptionSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> UserSubscription:
        """
        Create a new UserSubscription instance with validated data.
        """
        try:
            subscription = UserSubscription.objects.create(**validated_data)
            logger.info(f"Created subscription for user {subscription.user.username} (ID: {subscription.id})")
            return subscription
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise serializers.ValidationError(_("Failed to create subscription"))

    def update(self, instance: UserSubscription, validated_data: Dict[str, Any]) -> UserSubscription:
        """
        Update an existing UserSubscription instance with validated data.
        """
        try:
            allowed_fields = ['expire_time', 'keywords_extracted', 'keywords_extracted_percent']
            for attr, value in validated_data.items():
                if attr in allowed_fields:
                    setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated subscription for user {instance.user.username} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating subscription {instance.id}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update subscription"))

    def update_keyword_usage_action(self, instance: UserSubscription, keywords_used: int) -> Dict[str, Any]:
        """
        Custom action to update keyword usage and recalculate percentage.
        Can be used in views to handle keyword usage updates.
        """
        try:
            if instance.update_keyword_usage(keywords_used):
                instance.refresh_from_db()
                return self.to_representation(instance)
            logger.error(f"Failed to update keyword usage for subscription {instance.id}")
            raise serializers.ValidationError(_("Failed to update keyword usage"))
        except Exception as e:
            logger.error(f"Error in update_keyword_usage_action for subscription {instance.id}: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during keyword usage update"))

    def to_representation(self, instance: UserSubscription) -> Dict[str, Any]:
        """
        Customize the representation to include calculated fields and exclude write-only fields.
        """
        representation = super().to_representation(instance)
        representation.pop('user_id', None)
        representation.pop('subscription_plan_id', None)
        return representation
