import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from users.models import Organizer, Participant
from utils.choices import (
    EventType,
    EventStatus,
    DeliveryType,
    BaseSocialMedia,
    TopicCategory,
    EventRegistrationStatus,
)
from utils.utils import create_custom_image_file_path, generate_unique_slug


def get_event_image_path(instance, filename: str) -> str:
    """
    Custom file path for event images.
    """
    return create_custom_image_file_path(instance, filename, "images/events")


class BaseModel(models.Model):
    """
    An abstract base model with common fields for other models.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True

    def formatted_created_at(self) -> str:
        """
        Returns formatted creation timestamp.
        """
        return self.created_at.strftime("%d.%m.%Y %H:%M")


class Company(BaseModel):
    """
    Company model representing an organization.
    """

    name = models.CharField(max_length=50, verbose_name="Company")
    description = models.TextField(verbose_name="Company Description")
    website_url = models.URLField(max_length=200, blank=True, verbose_name="Company Website URL")
    slug = models.SlugField(db_index=True, editable=False, unique=True, verbose_name="Slug")

    class Meta(BaseModel.Meta):
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        """
        Save method with slug generation.
        """
        if not self.slug:
            self.slug = generate_unique_slug(self, field_name="name")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class CompanySocialMedia(BaseSocialMedia):
    """
    Social media links associated with a company.
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="social_media", verbose_name="Company Social Media"
    )

    class Meta(BaseSocialMedia.Meta):
        verbose_name = "Company Social Media Link"
        verbose_name_plural = "Company Social Media Links"
        unique_together = [("company", "platform")]


class Topic(models.Model):
    name = models.CharField(max_length=50, choices=TopicCategory.choices, unique=True)

    def __str__(self):
        return self.get_name_display()


class Event(BaseModel):
    """
    Represents an event.
    """

    title = models.CharField(max_length=255, verbose_name="Event Title")
    description = models.TextField(verbose_name="Event Description")
    event_start_time = models.TimeField(verbose_name="Start Time")
    event_end_time = models.TimeField(verbose_name="End Time", blank=True, null=True)
    event_start_date = models.DateField(verbose_name="Start Date")
    event_end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, verbose_name="City")
    country = models.CharField(max_length=50, blank=True, verbose_name="Country")
    location = models.CharField(max_length=255, verbose_name="Event Location")
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Maximum Capacity",
        help_text="The maximum number of participants for the event. Leave blank for unlimited.",
    )

    delivery_type = models.CharField(max_length=10, choices=DeliveryType.choices, verbose_name="Delivery Type")
    status = models.CharField(max_length=50, choices=EventStatus.choices, verbose_name="Event Status")
    event_type = models.CharField(max_length=50, choices=EventType.choices, verbose_name="Event Type")
    topics = models.ManyToManyField(Topic, related_name="events", verbose_name="Event Topics", blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="events", verbose_name="Company")
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name="events", verbose_name="Organizer")

    image = models.ImageField(blank=True, null=True, upload_to=get_event_image_path, verbose_name="Event Image")
    slug = models.SlugField(db_index=True, editable=False, unique=True, verbose_name="Slug")

    class Meta(BaseModel.Meta):
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-event_start_date", "event_start_time"]
        constraints = [
            models.CheckConstraint(
                check=Q(event_end_date__gte=F("event_start_date")) | Q(event_end_date__isnull=True),
                name="event_end_date_gte_event_start_date",
            ),
        ]

    def clean(self):
        """
        Validates the event's start date and time to ensure that the event is not set in the past.
        """
        if self.event_start_date and self.event_start_time:
            event_start_datetime = timezone.make_aware(
                timezone.datetime.combine(self.event_start_date, self.event_start_time)
            )
            if event_start_datetime < timezone.now():
                raise ValidationError("The event cannot start in the past.")
        super().clean()

    def save(self, *args, **kwargs):
        """
        Save method with slug generation.
        """
        if not self.slug:
            self.slug = generate_unique_slug(self, field_name="title")
        super().save(*args, **kwargs)

    @property
    def participants_count(self):
        """
        Returns the number of participants in the event.
        """
        return self.registrations.filter(status=EventRegistrationStatus.CONFIRMED).count()


    @property
    def available_capacity(self):
        """
        Returns the number of remaining available spots for this event.
        If capacity is not set (None or blank), the event is considered to have unlimited spots.
        """
        if self.capacity is None or self.capacity == 0:
            return None
        return self.capacity - self.participants_count

    def __str__(self) -> str:
        return f"{self.title} ({self.event_start_date} - {self.event_end_date})"


class EventSocialMedia(BaseSocialMedia):
    """
    Social media links associated with an event.
    """

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="social_media", verbose_name="Event Social Media"
    )

    class Meta(BaseSocialMedia.Meta):
        verbose_name = "Event Social Media Link"
        verbose_name_plural = "Event Social Media Links"
        unique_together = [("event", "platform")]


class EventRegistration(BaseModel):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="Participant", related_name="registrations"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Event", related_name="registrations")
    status = models.CharField(
        max_length=50,
        choices=EventRegistrationStatus.choices,
        default=EventRegistrationStatus.PENDING,
        verbose_name="Event Registration Status",
    )

    class Meta:
        unique_together = ("participant", "event")

    def save(self, *args, **kwargs):
        """
        Override save to handle the logic for available capacity.
        """
        if self.event.available_capacity is not None and self.event.available_capacity == 0:
            self.status = EventRegistrationStatus.WAITLIST
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.participant.user.email} registered for {self.event.title} - {self.status}"
