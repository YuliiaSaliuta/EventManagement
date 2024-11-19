from django.core.management.base import BaseCommand
from faker import Faker
import random

from events.models import Company, CompanySocialMedia

SOCIAL_MEDIA_PLATFORMS = ["telegram", "facebook", "twitter", "instagram", "linkedin", "youtube", "tiktok", "other"]


class Command(BaseCommand):
    help = "Create companies with their social media profiles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of companies to create",
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options["count"]

        self.stdout.write(f"Creating {count} companies...")

        for _ in range(count):
            # Create a company
            company = Company.objects.create(
                name=fake.company(),
                description=fake.text(),
                website_url=fake.url(),
            )

            # Create random social media profiles for the company
            num_social_media = random.randint(1, 5)
            selected_platforms = random.sample(SOCIAL_MEDIA_PLATFORMS, num_social_media)

            for platform in selected_platforms:
                url = fake.url()
                CompanySocialMedia.objects.get_or_create(
                    company=company,
                    platform=platform,
                    defaults={"url": url},
                )

            self.stdout.write(f"Created company: {company.name}")

        self.stdout.write("Finished creating companies.")
