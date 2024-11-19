import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.manager import CustomUserManager
from utils.choices import UserRole, BaseSocialMedia
from utils.utils import create_custom_image_file_path


def get_avatar_path(instance, filename: str) -> str:
    """
    Generate file path for user avatar images.
    """
    return create_custom_image_file_path(instance, filename, "images/avatars")


class User(AbstractUser):
    """
    Custom User model where email is used as the unique identifier instead of username.
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    username = None
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True, verbose_name="Email Address")
    avatar = models.ImageField(blank=True, null=True, upload_to=get_avatar_path, verbose_name="Avatar Image")
    phone = models.CharField(max_length=50, unique=True, verbose_name="Phone Number")

    def __str__(self) -> str:
        return f"{self.email}"

    def is_organizer(self):
        """
        Return True if the user is an organizer, otherwise False.
        """
        return hasattr(self, "organizer_profile")

    def is_participant(self):
        """
        Return True if the user is a participant, otherwise False.
        """
        return hasattr(self, "participant_profile")


class Participant(models.Model):
    """
    Model representing event participants.
    """

    ROLE = UserRole.PARTICIPANT

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participant_profile", verbose_name="User"
    )
    interests = models.ManyToManyField(
        "events.Topic", related_name="participants", verbose_name="Participant Interests", blank=True
    )
    attended_events = models.ManyToManyField(
        "events.Event", related_name="participants", blank=True, verbose_name="Attended Events"
    )

    def __str__(self) -> str:
        return f"Participant: {self.user}"


class Organizer(models.Model):
    """
    Model representing event organizers.
    """

    ROLE = UserRole.ORGANIZER

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizer_profile", verbose_name="User"
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biography")
    city = models.CharField(max_length=50, blank=True, verbose_name="City")
    country = models.CharField(max_length=50, blank=True, verbose_name="Country")

    def __str__(self) -> str:
        return f"Organizer: {self.user.email}"


class OrganizerSocialMedia(BaseSocialMedia):
    """
    Model for social media links of event organizers.
    """

    organizer = models.ForeignKey(
        Organizer, on_delete=models.CASCADE, related_name="social_media", verbose_name="Organizer Social Media"
    )

    class Meta(BaseSocialMedia.Meta):
        verbose_name = "Organizer Social Media Link"
        verbose_name_plural = "Organizer Social Media Links"
        unique_together = [("organizer", "platform")]
