from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import logging
from django.core.exceptions import ValidationError

# Configure logging for better debugging and monitoring
logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    """
    Abstract base model providing common timestamp fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """
        Override save method to include validation and logging.
        """
        try:
            self.full_clean()
            self.updated_at = timezone.now()
            super().save(*args, **kwargs)
            logger.info(f"Successfully saved {self.__class__.__name__} with ID: {self.id}")
        except ValidationError as e:
            logger.error(f"Validation error saving {self.__class__.__name__}: {str(e)}")
            raise


class CustomUser(AbstractUser, BaseModel):
    """
    Custom user model extending AbstractUser with additional fields and validation.
    """
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        verbose_name=_("Profile Image"),
        help_text=_("User's profile image"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['username']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self) -> str:
        """
        String representation of the CustomUser instance.
        """
        return self.username

    def clean(self) -> None:
        """
        Custom validation for CustomUser fields.
        """
        if self.profile_image:
            max_size = 5 * 1024 * 1024  # 5MB
            if self.profile_image.size > max_size:
                raise ValidationError(_("Profile image size must not exceed 5MB"))

    @classmethod
    def get_active_users(cls) -> list['CustomUser']:
        """
        Retrieve all active users.
        """
        try:
            return list(cls.objects.filter(is_active=True))
        except Exception as e:
            logger.error(f"Error retrieving active users: {str(e)}")
            return []


class Collaborator(BaseModel):
    """
    Collaborator model representing invitation-based relationships between users.
    """
    STATUS_CHOICES = (
        ('PENDING', _('Pending for Acceptance')),
        ('ACCEPT', _('Accepted Invitation')),
        ('REJECT', _('Rejected Invitation')),
    )

    invitation_sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        verbose_name=_("Invitation Sender"),
        help_text=_("User who sent the invitation"),
    )
    invitation_receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_invitations',
        verbose_name=_("Invitation Receiver"),
        help_text=_("User who received the invitation"),
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_("Status"),
        help_text=_("Current status of the invitation"),
    )

    class Meta:
        verbose_name = _("Collaborator")
        verbose_name_plural = _("Collaborators")
        unique_together = ('invitation_sender', 'invitation_receiver')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['invitation_sender', 'invitation_receiver']),
        ]

    def __str__(self) -> str:
        """
        String representation of the Collaborator instance.
        """
        return f"{self.invitation_sender} -> {self.invitation_receiver} ({self.status})"

    def clean(self) -> None:
        """
        Custom validation for Collaborator fields.
        """
        if self.invitation_sender == self.invitation_receiver:
            raise ValidationError(_("A user cannot send an invitation to themselves"))
        if Collaborator.objects.filter(
            invitation_sender=self.invitation_receiver,
            invitation_receiver=self.invitation_sender,
            status='PENDING'
        ).exists():
            raise ValidationError(_("A pending invitation already exists in the opposite direction"))

    def accept_invitation(self) -> bool:
        """
        Accept the collaboration invitation with transaction safety.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status == 'PENDING':
                    self.status = 'ACCEPT'
                    self.save()
                    logger.info(f"Invitation accepted: {self}")
                    return True
                logger.warning(f"Cannot accept invitation with status: {self.status}")
                return False
        except Exception as e:
            logger.error(f"Error accepting invitation: {str(e)}")
            return False

    def reject_invitation(self) -> bool:
        """
        Reject the collaboration invitation with transaction safety.
        """
        from django.db import transaction

        try:
            with transaction.atomic():
                if self.status == 'PENDING':
                    self.status = 'REJECT'
                    self.save()
                    logger.info(f"Invitation rejected: {self}")
                    return True
                logger.warning(f"Cannot reject invitation with status: {self.status}")
                return False
        except Exception as e:
            logger.error(f"Error rejecting invitation: {str(e)}")
            return False