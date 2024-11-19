from django.core.management.base import BaseCommand

from events.models import Topic
from users.models import User, Participant, Organizer, OrganizerSocialMedia
from faker import Faker
import random

fake = Faker()

SOCIAL_MEDIA_PLATFORMS = ["telegram", "facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok", "other"]


class Command(BaseCommand):
    help = "Generate users with Participant or Organizer profiles, including OrganizerSocialMedia for organizers"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, help="Number of users to create", default=10)
        parser.add_argument(
            "--role", type=str, choices=["participant", "organizer"], help="Role of users", required=True
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        role = kwargs["role"]

        self.stdout.write(f"Creating {count} {role} users...")

        count = kwargs["count"]

        # Отримати всі доступні теми
        topics = list(Topic.objects.all())

        if not topics:
            self.stdout.write(self.style.ERROR("No topics available. Please run `create_topics` command first."))
            return

        for _ in range(count):
            email = fake.unique.email()
            phone = fake.unique.phone_number()
            first_name = fake.first_name()
            last_name = fake.last_name()

            # Create user
            user = User.objects.create_user(
                email=email, password="StrongPassword123!", phone=phone, first_name=first_name, last_name=last_name
            )

            if role == "participant":
                participant = Participant.objects.create(user=user)

                # Create random interests (from 1 to 5 interests)
                num_interests = random.randint(1, 5)
                interests = random.sample(topics, num_interests)
                participant.interests.set(interests)

            elif role == "organizer":
                organizer = Organizer.objects.create(
                    user=user, bio=fake.text(), city=fake.city(), country=fake.country()
                )

                # Create random social media profiles for the organizer
                num_social_media = random.randint(1, 5)
                selected_platforms = random.sample(SOCIAL_MEDIA_PLATFORMS, num_social_media)
                for platform in selected_platforms:
                    url = fake.url()
                    OrganizerSocialMedia.objects.get_or_create(
                        organizer=organizer,
                        platform=platform,
                        defaults={"url": url},
                    )
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} {role} users!"))
