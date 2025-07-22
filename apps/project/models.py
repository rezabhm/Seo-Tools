from typing import List, Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
from apps.core.models import BaseModel, CustomUser, Collaborator

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)

class Project(BaseModel):
    """
    Project model representing a user-managed project with collaborators and metadata.
    """
    name = models.CharField(
        max_length=50,
        verbose_name=_("Project Name"),
        help_text=_("Name of the project (max 50 characters)"),
    )
    description = models.TextField(
        verbose_name=_("Project Description"),
        help_text=_("Detailed description of the project"),
    )
    service_url = models.URLField(
        max_length=250,
        verbose_name=_("Service URL"),
        help_text=_("URL for the project's service or landing page"),
    )
    banner = models.ImageField(
        upload_to='project_banners/',
        null=True,
        blank=True,
        verbose_name=_("Project Banner"),
        help_text=_("Banner image for the project"),
    )
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name=_("Project Owner"),
        help_text=_("User who owns the project"),
    )
    collaborators = models.ManyToManyField(
        Collaborator,
        related_name='projects',
        blank=True,
        verbose_name=_("Collaborators"),
        help_text=_("Collaborators associated with the project"),
    )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'owner'],
                name='unique_project_name_per_owner'
            ),
        ]

    def __str__(self) -> str:
        """
        String representation of the Project instance.
        """
        return f"{self.name} (Owner: {self.owner.username})"

    def clean(self) -> None:
        """
        Custom validation for Project fields.
        """
        if not self.name.strip():
            raise ValidationError(_("Project name cannot be empty"))
        if self.banner:
            max_size = 5 * 1024 * 1024  # 5MB
            if self.banner.size > max_size:
                raise ValidationError(_("Banner image size must not exceed 5MB"))
        if not self.service_url.startswith(('http://', 'https://')):
            raise ValidationError(_("Service URL must start with http:// or https://"))

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to include validation and logging.
        """
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved Project: {self.name} (ID: {self.id})")
        except ValidationError as e:
            logger.error(f"Validation error saving Project: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving Project: {str(e)}")
            raise

    def add_collaborator(self, collaborator: Collaborator) -> bool:
        """
        Add a collaborator to the project with transaction safety.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if collaborator.invitation_sender == self.owner or collaborator.invitation_receiver == self.owner:
                    raise ValidationError(_("Project owner cannot be added as a collaborator"))
                if collaborator.status != 'accepted':
                    raise ValidationError(_("Only accepted collaborators can be added to a project"))
                self.collaborators.add(collaborator)
                logger.info(f"Added collaborator {collaborator} to project {self.name}")
                return True
        except Exception as e:
            logger.error(f"Error adding collaborator to project {self.name}: {str(e)}")
            return False

    @classmethod
    def get_user_projects(cls, user: CustomUser) -> List['Project']:
        """
        Retrieve all projects owned by or collaborated on by a user.
        """
        try:
            return list(cls.objects.filter(
                models.Q(owner=user) | models.Q(collaborators__invitation_sender=user) | 
                models.Q(collaborators__invitation_receiver=user)
            ).distinct())
        except Exception as e:
            logger.error(f"Error retrieving projects for user {user.username}: {str(e)}")
            return []


class Process(BaseModel):
    """
    Process model representing a processing task associated with a project.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('started', _('Started')),
        ('finished', _('Finished')),
    )

    extraction_level = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Extraction Level"),
        help_text=_("Level of data extraction for the process"),
    )
    total_count = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Total Progress Count"),
        help_text=_("Total number of items to process"),
    )
    completed_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Completed Progress Count"),
        help_text=_("Number of items processed so far"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Status"),
        help_text=_("Current status of the process"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='processes',
        verbose_name=_("Project"),
        help_text=_("Associated project for this process"),
    )

    class Meta:
        verbose_name = _("Process")
        verbose_name_plural = _("Processes")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['project']),
        ]

    def __str__(self) -> str:
        """
        String representation of the Process instance.
        """
        return f"Process for {self.project.name} ({self.status})"

    def clean(self) -> None:
        """
        Custom validation for Process fields.
        """
        if self.extraction_level < 0:
            raise ValidationError(_("Extraction level cannot be negative"))
        if self.total_count < 1:
            raise ValidationError(_("Total progress count must be at least 1"))
        if self.completed_count < 0:
            raise ValidationError(_("Completed progress count cannot be negative"))
        if self.completed_count > self.total_count:
            raise ValidationError(_("Completed count cannot exceed total count"))
        if self.status not in dict(self.STATUS_CHOICES).keys():
            raise ValidationError(_("Invalid process status"))

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to include validation and logging.
        """
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved Process for project {self.project.name} (ID: {self.id})")
        except ValidationError as e:
            logger.error(f"Validation error saving Process: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving Process: {str(e)}")
            raise

    def update_progress(self, increment: int) -> bool:
        """
        Update the process progress with transaction safety.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                self.completed_count = models.F('completed_count') + increment
                if self.completed_count >= self.total_count:
                    self.status = 'finished'
                elif self.status == 'pending':
                    self.status = 'started'
                self.save()
                self.refresh_from_db()
                logger.info(f"Updated progress for process {self.id} in project {self.project.name}")
                return True
        except Exception as e:
            logger.error(f"Error updating progress for process {self.id}: {str(e)}")
            return False

    @classmethod
    def get_active_processes(cls, project: Project) -> List['Process']:
        """
        Retrieve all active (pending or started) processes for a given project.
        """
        try:
            return list(cls.objects.filter(project=project, status__in=['pending', 'started']))
        except Exception as e:
            logger.error(f"Error retrieving active processes for project {project.name}: {str(e)}")
            return []