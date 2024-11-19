from datetime import timedelta

from django.core.management.base import BaseCommand
from faker import Faker
import random
from events.models import Company, Topic, Event, EventSocialMedia
from users.models import Organizer

SOCIAL_MEDIA_PLATFORMS = ["telegram", "facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok", "other"]

EVENT_STATUSES = ["UPCOMING", "ONGOING", "COMPLETED", "CANCELLED"]
DELIVERY_TYPES = ["ONLINE", "OFFLINE", "HYBRID"]
EVENT_TYPES = [
    "MEETING",
    "CONFERENCE",
    "WORKSHOP",
    "SEMINAR",
    "WEBINAR",
    "TRAINING",
    "EXPO",
    "FESTIVAL",
    "PANEL_DISCUSSION",
    "NETWORKING_EVENT",
    "PRODUCT_LAUNCH",
    "VIRTUAL_CONFERENCE",
    "Q_A_SESSION",
    "HACKATHON",
    "MEETUP",
    "CONVENTION",
    "SYMPOSIUM",
    "RETREAT",
    "GALA",
    "OTHER",
]


class Command(BaseCommand):
    help = "Create events with their social media profiles and related data"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=5, help="Number of events to create")

    def handle(self, *args, **options):
        fake = Faker()
        count = options["count"]

        self.stdout.write(f"Creating {count} events...")

        # Get existing companies, organizers, and topics
        companies = list(Company.objects.all())
        organizers = list(Organizer.objects.all())
        topics = list(Topic.objects.all())

        if not companies or not organizers or not topics:
            self.stdout.write(
                "Ensure you have some companies, organizers, and topics in the database before running this command."
            )
            return

        for _ in range(count):
            # Randomly select a company and organizer
            company = random.choice(companies)
            organizer = random.choice(organizers)
            event_start_date = fake.date_this_year(before_today=False, after_today=True)
            event_end_date = event_start_date + timedelta(days=random.randint(0, 5))
            event_start_time = fake.time()
            event_end_time = fake.time() if random.choice([True, False]) else None

            # Generate random event data
            title = fake.sentence(nb_words=5)
            event = Event.objects.create(
                title=title,
                description=fake.text(),
                event_start_time=event_start_time,
                event_end_time=event_end_time,
                event_start_date=event_start_date,
                event_end_date=event_end_date,
                city=fake.city(),
                country=fake.country(),
                location=fake.address(),
                capacity=random.randint(1, 500),
                delivery_type=random.choice(DELIVERY_TYPES),
                status=random.choice(EVENT_STATUSES),
                event_type=random.choice(EVENT_TYPES),
                company=company,
                organizer=organizer,
            )

            # Add random topics
            selected_topics = random.sample(topics, random.randint(1, 3))
            event.topics.add(*selected_topics)

            # Create random social media profiles for the event
            num_social_media = random.randint(1, 5)
            selected_platforms = random.sample(SOCIAL_MEDIA_PLATFORMS, num_social_media)

            for platform in selected_platforms:
                EventSocialMedia.objects.create(
                    event=event,
                    platform=platform,
                    url=fake.url(),
                )

            self.stdout.write(f"Created event: {event.title}")

        self.stdout.write("Finished creating events.")
