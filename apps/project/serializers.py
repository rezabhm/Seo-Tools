# Django REST Framework serializers for Project and Process models
# Author: [Your Name]
# Date: July 22, 2025
# Description: Serializers for handling API representation and validation of project and process data, including progress calculations

from typing import Dict, Any, List
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import logging
from apps.core.models import BaseModel, CustomUser, Collaborator
from apps.project.models import Project, Process
from apps.core.serializers import CustomUserSerializer, CollaboratorSerializer

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model, handling project data and relationships.
    """
    owner = CustomUserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='owner',
        write_only=True,
        required=True,
        help_text=_("ID of the project owner")
    )
    collaborators = CollaboratorSerializer(many=True, read_only=True)
    collaborator_ids = serializers.PrimaryKeyRelatedField(
        queryset=Collaborator.objects.all(),
        source='collaborators',
        many=True,
        write_only=True,
        required=False,
        help_text=_("List of collaborator IDs")
    )
    banner = serializers.ImageField(
        required=False,
        allow_null=True,
        max_length=100,
        use_url=True
    )

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'service_url', 'banner',
            'owner', 'owner_id', 'collaborators', 'collaborator_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner', 'collaborators']

    def validate_name(self, value: str) -> str:
        """
        Validate the project name.
        """
        if not value.strip():
            logger.error("Project name provided is empty")
            raise serializers.ValidationError(_("Project name cannot be empty"))
        if len(value) > 50:
            logger.error(f"Project name exceeds 50 characters: {value}")
            raise serializers.ValidationError(_("Project name cannot exceed 50 characters"))
        return value

    def validate_service_url(self, value: str) -> str:
        """
        Validate the service URL.
        """
        if not value.startswith(('http://', 'https://')):
            logger.error(f"Invalid service URL: {value}")
            raise serializers.ValidationError(_("Service URL must start with http:// or https://"))
        return value

    def validate_banner(self, value: Any) -> Any:
        """
        Validate the banner image size.
        """
        if value:
            max_size = 5 * 1024 * 1024  # 5MB
            if value.size > max_size:
                logger.error(f"Banner image size exceeds 5MB for project")
                raise serializers.ValidationError(_("Banner image size must not exceed 5MB"))
        return value

    def validate_collaborator_ids(self, value: List[Collaborator]) -> List[Collaborator]:
        """
        Validate that collaborators are accepted and not the project owner.
        """
        for collaborator in value:
            if collaborator.status != 'accepted':
                logger.error(f"Non-accepted collaborator provided: {collaborator}")
                raise serializers.ValidationError(_("Only accepted collaborators can be added to a project"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the Project instance.
        """
        try:
            instance = Project(**data)
            instance.clean()
            if 'owner' in data and 'collaborators' in data:
                for collaborator in data['collaborators']:
                    if collaborator.invitation_sender == data['owner'] or collaborator.invitation_receiver == data['owner']:
                        logger.error(f"Owner cannot be added as a collaborator: {data['owner']}")
                        raise serializers.ValidationError(_("Project owner cannot be added as a collaborator"))
            return data
        except ValidationError as e:
            logger.error(f"Validation error in ProjectSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in ProjectSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> Project:
        """
        Create a new Project instance with validated data.
        """
        try:
            collaborator_ids = validated_data.pop('collaborators', [])
            project = Project.objects.create(**validated_data)
            if collaborator_ids:
                project.collaborators.set(collaborator_ids)
            logger.info(f"Created project: {project.name} (ID: {project.id})")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise serializers.ValidationError(_("Failed to create project"))

    def update(self, instance: Project, validated_data: Dict[str, Any]) -> Project:
        """
        Update an existing Project instance with validated data.
        """
        try:
            collaborator_ids = validated_data.pop('collaborators', None)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if collaborator_ids is not None:
                instance.collaborators.set(collaborator_ids)
            logger.info(f"Updated project: {instance.name} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating project {instance.name}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update project"))

    def to_representation(self, instance: Project) -> Dict[str, Any]:
        """
        Customize the representation to exclude write-only fields.
        """
        representation = super().to_representation(instance)
        representation.pop('owner_id', None)
        representation.pop('collaborator_ids', None)
        return representation

class ProcessSerializer(serializers.ModelSerializer):
    """
    Serializer for the Process model, handling process data with progress calculations.
    """
    project = serializers.StringRelatedField(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True,
        required=True,
        help_text=_("ID of the associated project")
    )
    progress_percentage = serializers.SerializerMethodField(
        help_text=_("Percentage of process completion")
    )

    class Meta:
        model = Process
        fields = [
            'id', 'extraction_level', 'total_count', 'completed_count',
            'status', 'project', 'project_id', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'project', 'progress_percentage']

    def get_progress_percentage(self, obj: Process) -> float:
        """
        Calculate the progress percentage as (completed_count / total_count) * 100.
        """
        try:
            if obj.total_count > 0:
                percentage = (obj.completed_count / obj.total_count) * 100
                return round(percentage, 2)
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating progress percentage for process {obj.id}: {str(e)}")
            return 0.0

    def validate_extraction_level(self, value: int) -> int:
        """
        Validate the extraction_level field.
        """
        if value < 0:
            logger.error(f"Negative extraction level provided: {value}")
            raise serializers.ValidationError(_("Extraction level cannot be negative"))
        return value

    def validate_total_count(self, value: int) -> int:
        """
        Validate the total_count field.
        """
        if value < 1:
            logger.error(f"Invalid total count provided: {value}")
            raise serializers.ValidationError(_("Total progress count must be at least 1"))
        return value

    def validate_completed_count(self, value: int) -> int:
        """
        Validate the completed_count field.
        """
        if value < 0:
            logger.error(f"Negative completed count provided: {value}")
            raise serializers.ValidationError(_("Completed progress count cannot be negative"))
        return value

    def validate_status(self, value: str) -> str:
        """
        Validate the status field.
        """
        if value not in dict(Process.STATUS_CHOICES):
            logger.error(f"Invalid status provided: {value}")
            raise serializers.ValidationError(_("Invalid process status"))
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform object-level validation for the Process instance.
        """
        try:
            if 'completed_count' in data and 'total_count' in data:
                if data['completed_count'] > data['total_count']:
                    logger.error(f"Completed count {data['completed_count']} exceeds total count {data['total_count']}")
                    raise serializers.ValidationError(_("Completed count cannot exceed total count"))
            instance = Process(**data)
            instance.clean()
            return data
        except ValidationError as e:
            logger.error(f"Validation error in ProcessSerializer: {str(e)}")
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in ProcessSerializer validation: {str(e)}")
            raise serializers.ValidationError(_("An unexpected error occurred during validation"))

    def create(self, validated_data: Dict[str, Any]) -> Process:
        """
        Create a new Process instance with validated data.
        """
        try:
            process = Process.objects.create(**validated_data)
            logger.info(f"Created process for project {process.project.name} (ID: {process.id})")
            return process
        except Exception as e:
            logger.error(f"Error creating process: {str(e)}")
            raise serializers.ValidationError(_("Failed to create process"))

    def update(self, instance: Process, validated_data: Dict[str, Any]) -> Process:
        """
        Update an existing Process instance with validated data.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated process for project {instance.project.name} (ID: {instance.id})")
            return instance
        except Exception as e:
            logger.error(f"Error updating process {instance.id}: {str(e)}")
            raise serializers.ValidationError(_("Failed to update process"))

    def to_representation(self, instance: Process) -> Dict[str, Any]:
        """
        Customize the representation to include progress percentage and exclude project_id.
        """
        representation = super().to_representation(instance)
        representation.pop('project_id', None)
        representation['progress_count'] = representation['completed_count'] / representation['total_count']
        return representation
