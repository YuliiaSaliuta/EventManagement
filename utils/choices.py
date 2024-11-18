from django.db import models


class UserRole(models.TextChoices):
    ORGANIZER = "ORGANIZER", "Event Organizer"
    PARTICIPANT = "PARTICIPANT", "Participant"


class EventStatus(models.TextChoices):
    UPCOMING = "UPCOMING", "Upcoming"
    ONGOING = "ONGOING", "Ongoing"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class EventRegistrationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"
    WAITLIST = "WAITLIST", "Waitlist"


class DeliveryType(models.TextChoices):
    ONLINE = "ONLINE", "Online"
    OFFLINE = "OFFLINE", "Offline"
    HYBRID = "HYBRID", "Hybrid"


class EventType(models.TextChoices):
    MEETING = "MEETING", "Meeting"
    CONFERENCE = "CONFERENCE", "Conference"
    WORKSHOP = "WORKSHOP", "Workshop"
    SEMINAR = "SEMINAR", "Seminar"
    WEBINAR = "WEBINAR", "Webinar"
    TRAINING = "TRAINING", "Training"
    EXPO = "EXPO", "Expo"
    FESTIVAL = "FESTIVAL", "Festival"
    PANEL_DISCUSSION = "PANEL_DISCUSSION", "Panel Discussion"
    NETWORKING_EVENT = "NETWORKING_EVENT", "Networking Event"
    PRODUCT_LAUNCH = "PRODUCT_LAUNCH", "Product Launch"
    VIRTUAL_CONFERENCE = "VIRTUAL_CONFERENCE", "Virtual Conference"
    Q_A_SESSION = "Q_A_SESSION", "Q&A Session"
    HACKATHON = "HACKATHON", "Hackathon"
    MEETUP = "MEETUP", "Meetup"
    CONVENTION = "CONVENTION", "Convention"
    SYMPOSIUM = "SYMPOSIUM", "Symposium"
    RETREAT = "RETREAT", "Retreat"
    GALA = "GALA", "Gala"
    OTHER = "OTHER", "Other"


class TopicCategory(models.TextChoices):
    TECHNOLOGY = "TECHNOLOGY", "Technology"
    SCIENCE = "SCIENCE", "Science"
    BUSINESS = "BUSINESS", "Business"
    EDUCATION = "EDUCATION", "Education"
    HEALTH = "HEALTH", "Health"
    ART = "ART", "Art"
    ENTERTAINMENT = "ENTERTAINMENT", "Entertainment"
    SPORTS = "SPORTS", "Sports"
    ENVIRONMENT = "ENVIRONMENT", "Environment"
    FINANCE = "FINANCE", "Finance"
    MARKETING = "MARKETING", "Marketing"
    LAW = "LAW", "Law"
    POLITICS = "POLITICS", "Politics"
    CULTURE = "CULTURE", "Culture"
    LIFESTYLE = "LIFESTYLE", "Lifestyle"
    TRAVEL = "TRAVEL", "Travel"
    FOOD = "FOOD", "Food"
    MUSIC = "MUSIC", "Music"
    DESIGN = "DESIGN", "Design"
    SOCIAL_IMPACT = "SOCIAL_IMPACT", "Social Impact"
    PHILANTHROPY = "PHILANTHROPY", "Philanthropy"
    PERSONAL_DEVELOPMENT = "PERSONAL_DEVELOPMENT", "Personal Development"
    OTHER = "OTHER", "Other"


class BaseSocialMedia(models.Model):
    platform = models.CharField(
        max_length=50,
        choices=[
            ("telegram", "Telegram"),
            ("facebook", "Facebook"),
            ("twitter", "Twitter"),
            ("instagram", "Instagram"),
            ("linkedin", "LinkedIn"),
            ("youtube", "YouTube"),
            ("tiktok", "TikTok"),
            ("other", "Other"),
        ],
        default="other",
        verbose_name="Platform",
    )
    url = models.URLField(max_length=512, verbose_name="Social Media URL")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.platform} - {self.url}"
