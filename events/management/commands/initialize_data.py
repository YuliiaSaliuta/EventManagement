from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all data initialization commands in the correct order"

    def handle(self, *args, **options):
        self.stdout.write("Starting data initialization...")

        try:
            # 1. Create topics
            self.stdout.write("Running create_topics...")
            call_command("create_topics")

            # 2. Create participants
            self.stdout.write("Running create_users for participants...")
            call_command("create_users", "--count", 20, "--role", "participant")

            # 3. Create organizers
            self.stdout.write("Running create_users for organizers...")
            call_command("create_users", "--count", 5, "--role", "organizer")

            # 4. Create companies
            self.stdout.write("Running create_companies...")
            call_command("create_companies", "--count", 10)

            # 5. Create events
            self.stdout.write("Running create_events...")
            call_command("create_events", "--count", 15)

            # 6. Create event registrations
            self.stdout.write("Running create_event_registrations...")
            call_command("create_event_registrations", "--count", 20)

            self.stdout.write(self.style.SUCCESS("All commands executed successfully!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during data initialization: {e}"))
