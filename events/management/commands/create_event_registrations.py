import random
from django.core.management.base import BaseCommand
from events.models import Event, EventRegistration, Participant
from utils.choices import EventRegistrationStatus


class Command(BaseCommand):
    help = "Generate random event registrations"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10, help="Number of registrations to create")

    def handle(self, *args, **options):
        count = options["count"]
        participants = list(Participant.objects.all())
        events = list(Event.objects.all())

        if not participants:
            self.stdout.write(self.style.WARNING("No participants found. Create participants first."))
            return

        if not events:
            self.stdout.write(self.style.WARNING("No events found. Create events first."))
            return

        self.stdout.write(f"Creating {count} event registrations...")

        created_count = 0
        for _ in range(count):
            participant = random.choice(participants)
            event = random.choice(events)

            if EventRegistration.objects.filter(participant=participant, event=event).exists():
                continue

            status = random.choices(list(EventRegistrationStatus.values), weights=[70, 20, 5, 3, 2], k=1)[0]

            EventRegistration.objects.create(participant=participant, event=event, status=status)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} event registrations."))
