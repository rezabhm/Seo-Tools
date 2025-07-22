from typing import List
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import logging
from apps.core.models import BaseModel
from apps.project.models import Project

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class Keyword(BaseModel):
    """
    Keyword model representing SEO keywords with associated metadata.
    Follows clean code principles with comprehensive validation and documentation.
    """
    KEYWORD_TYPE_CHOICES = (
        ('standard', _('Standard')),
        ('prefix', _('Prefix')),
        ('suffix', _('Suffix')),
    )

    root_keyword = models.CharField(
        max_length=128,
        verbose_name=_("Root Keyword"),
        help_text=_("Primary keyword or phrase (max 128 characters)"),
    )
    keyword = models.CharField(
        max_length=256,
        verbose_name=_("Keyword"),
        help_text=_("Full keyword including variations (max 256 characters)"),
    )
    keyword_type = models.CharField(
        max_length=64,
        choices=KEYWORD_TYPE_CHOICES,
        default='standard',
        verbose_name=_("Keyword Type"),
        help_text=_("Type of keyword (standard, prefix, or suffix)"),
    )
    extra_word = models.CharField(
        max_length=32,
        default='',
        blank=True,
        verbose_name=_("Extra Word"),
        help_text=_("Additional word or modifier for the keyword (max 32 characters)"),
    )
    search_volume_data = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Search Volume Data"),
        help_text=_("JSON data containing search volume metrics"),
    )
    geo_search_volume_data = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Geographic Search Volume Data"),
        help_text=_("JSON data containing geographic search volume metrics"),
    )
    search_engine_results = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Search Engine Results"),
        help_text=_("JSON data containing search engine results data"),
    )
    search_volume = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Search Volume"),
        help_text=_("Total search volume for the keyword"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='keywords',
        verbose_name=_("Project"),
        help_text=_("Associated project for this keyword"),
    )

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")
        ordering = ['keyword']
        indexes = [
            models.Index(fields=['root_keyword']),
            models.Index(fields=['keyword']),
            models.Index(fields=['keyword_type']),
            models.Index(fields=['project']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['keyword', 'project'],
                name='unique_keyword_per_project'
            ),
        ]

    def __str__(self) -> str:
        """
        String representation of the Keyword instance.
        """
        return f"{self.keyword} (Vol: {self.search_volume})"

    def clean(self) -> None:
        """
        Custom validation for Keyword fields.
        """
        if not self.root_keyword.strip():
            raise ValidationError(_("Root keyword cannot be empty"))
        if len(self.root_keyword) > 512:
            raise ValidationError(_("Root keyword cannot exceed 128 characters"))
        if len(self.keyword) > 1028:
            raise ValidationError(_("Keyword cannot exceed 256 characters"))
        if self.extra_word and len(self.extra_word) > 32:
            raise ValidationError(_("Extra word cannot exceed 32 characters"))
        if self.search_volume < 0:
            raise ValidationError(_("Search volume cannot be negative"))

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to include validation and logging.
        """
        try:
            self.full_clean()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved Keyword: {self.keyword} (ID: {self.id})")
        except ValidationError as e:
            logger.error(f"Validation error saving Keyword: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving Keyword: {str(e)}")
            raise

    @classmethod
    def get_keywords_by_project(cls, project_id: int) -> List['Keyword']:
        """
        Retrieve all keywords associated with a specific project.
        """
        try:
            return list(cls.objects.filter(project_id=project_id))
        except Exception as e:
            logger.error(f"Error retrieving keywords for project {project_id}: {str(e)}")
            return []

    @classmethod
    def get_high_volume_keywords(cls, threshold: int = 1000) -> List['Keyword']:
        """
        Retrieve keywords with search volume above the specified threshold.
        """
        try:
            return list(cls.objects.filter(search_volume__gte=threshold))
        except Exception as e:
            logger.error(f"Error retrieving high volume keywords: {str(e)}")
            return []