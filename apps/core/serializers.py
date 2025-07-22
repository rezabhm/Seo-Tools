from typing import Dict, Any
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import logging
from apps.core.models import CustomUser, Collaborator

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model, handling user data and profile image.
    """
    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
        max_length=100,
        use_url=True
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile_image', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active']

    def validate_profile_image(self, value: Any) -> Any:
        """
        Validate the profile image size and format.
        """
        if value:
            max_size = 5 * 1024 * 1024  # 5MB
            if value.size > max_size:
                logger.error(f"Profile image size exceeds 5MB for user {self.instance.username if self.instance else 'new user'}")
                raise serializers.ValidationError(_("Profile image size must not exceed 5MB"))
        return value

    def validate_email(self, value: str) -> str:
        """
        Ensure email is unique and properly formatted.
        """
        if CustomUser.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            logger.error(f"Attempt to use duplicate email: {value}")
            raise serializers.ValidationError(_("This email is already in use"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the CustomUser instance.
        """
        try:
            instance = CustomUser(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in CustomUserSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in CustomUserSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Create a new CustomUser instance with validated data.
        """
        try:
            user = CustomUser.objects.create_user(**validated_data)
            logger.info(f"Created new user: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise serializers.ValidationError(_("Failed to create user"))

    def update(self, instance: CustomUser, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Update an existing CustomUser instance with validated data.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated user: {instance.username}")
            return instance
        except Exception as e:
            logger.error(f"Error updating user {instance.username}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update user"))


class CollaboratorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Collaborator model, handling invitation relationships between users.
    """
    invitation_sender = CustomUserSerializer(read_only=True)
    invitation_receiver = CustomUserSerializer(read_only=True)
    invitation_sender_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='invitation_sender',
        write_only=True,
        required=True
    )
    invitation_receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='invitation_receiver',
        write_only=True,
        required=True
    )

    class Meta:
        model = Collaborator
        fields = [
            'id', 'invitation_sender', 'invitation_receiver',
            'invitation_sender_id', 'invitation_receiver_id',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the Collaborator instance.
        """
        try:
            instance = Collaborator(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in CollaboratorSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in CollaboratorSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> Collaborator:
        """
        Create a new Collaborator instance with validated data.
        """
        try:
            collaborator = Collaborator.objects.create(**validated_data)
            logger.info(f"Created collaborator invitation: {collaborator}")
            return collaborator
        except Exception as e:
            logger.error(f"Error creating collaborator: {str(e)}")
            raise serializers.ValidationError(_("Failed to create collaborator"))

    def update(self, instance: Collaborator, validated_data: Dict[str, Any]) -> Collaborator:
        """
        Update an existing Collaborator instance with validated data.
        """
        try:
            # Only allow updating status for existing invitations
            allowed_fields = ['status']
            for attr, value in validated_data.items():
                if attr in allowed_fields:
                    setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated collaborator: {instance}")
            return instance
        except Exception as e:
            logger.error(f"Error updating collaborator {instance}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update collaborator"))

    def validate_status(self, value: str) -> str:
        """
        Validate the status field to ensure it matches allowed choices.
        """
        if value not in dict(Collaborator.STATUS_CHOICES):
            logger.error(f"Invalid status provided: {value}")
            raise serializers.ValidationError(_("Invalid status value"))
        return value

    def to_representation(self, instance: Collaborator) -> Dict[str, Any]:
        """
        Customize the representation to include nested user data.
        """
        representation = super().to_representation(instance)
        representation.pop('invitation_sender_id', None)
        representation.pop('invitation_receiver_id', None)
        return representation