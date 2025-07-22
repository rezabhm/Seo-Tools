from typing import Dict, Any, List
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import logging
from apps.keyword_service.models import Keyword
from apps.project.models import Project

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class KeywordSerializer(serializers.ModelSerializer):
    """
    Serializer for the Keyword model, handling SEO keyword data and metadata.
    """
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True,
        required=True,
        help_text=_("ID of the associated project")
    )
    project = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Keyword
        fields = [
            'id', 'root_keyword', 'keyword', 'keyword_type', 'extra_word',
            'search_volume_data', 'geo_search_volume_data', 'search_engine_results',
            'search_volume', 'project', 'project_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'project']

    def validate_root_keyword(self, value: str) -> str:
        """
        Validate the root_keyword field.
        """
        if not value.strip():
            logger.error("Root keyword provided is empty")
            raise serializers.ValidationError(_("Root keyword cannot be empty"))
        if len(value) > 128:
            logger.error(f"Root keyword exceeds 128 characters: {value}")
            raise serializers.ValidationError(_("Root keyword cannot exceed 128 characters"))
        return value

    def validate_keyword(self, value: str) -> str:
        """
        Validate the keyword field.
        """
        if len(value) > 256:
            logger.error(f"Keyword exceeds 256 characters: {value}")
            raise serializers.ValidationError(_("Keyword cannot exceed 256 characters"))
        return value

    def validate_extra_word(self, value: str) -> str:
        """
        Validate the extra_word field.
        """
        if value and len(value) > 32:
            logger.error(f"Extra word exceeds 32 characters: {value}")
            raise serializers.ValidationError(_("Extra word cannot exceed 32 characters"))
        return value

    def validate_search_volume(self, value: int) -> int:
        """
        Validate the search_volume field.
        """
        if value < 0:
            logger.error(f"Negative search volume provided: {value}")
            raise serializers.ValidationError(_("Search volume cannot be negative"))
        return value

    def validate_keyword_type(self, value: str) -> str:
        """
        Validate the keyword_type field.
        """
        if value not in dict(Keyword.KEYWORD_TYPE_CHOICES):
            logger.error(f"Invalid keyword type provided: {value}")
            raise serializers.ValidationError(_("Invalid keyword type"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the Keyword instance.
        """
        try:
            instance = Keyword(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in KeywordSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in KeywordSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> Keyword:
        """
        Create a new Keyword instance with validated data.
        """
        try:
            keyword = Keyword.objects.create(**validated_data)
            logger.info(f"Created keyword: {keyword.keyword} (ID: {keyword.id})")
            return keyword
        except Exception as e:
            logger.error(f"Error creating keyword: {str(e)}")
            raise serializers.ValidationError(_("Failed to create keyword"))

    def update(self, instance: Keyword, validated_data: Dict[str, Any]) -> Keyword:
        """
        Update an existing Keyword instance with validated data.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated keyword: {instance.keyword} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating keyword {instance.keyword}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update keyword"))

    def to_representation(self, instance: Keyword) -> Dict[str, Any]:
        """
        Customize the representation to exclude project_id from the output.
        """
        representation = super().to_representation(instance)
        representation.pop('project_id', None)
        return representation

    @classmethod
    def get_high_volume_keywords(cls, threshold: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve serialized data for keywords with search volume above the threshold.
        """
        try:
            keywords = Keyword.get_high_volume_keywords(threshold)
            return cls(many=True).to_representation(keywords)
        except Exception as e:
            logger.error(f"Error retrieving high volume keywords: {str(e)}")
            return []