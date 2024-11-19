from django.core.management.base import BaseCommand
from events.models import Topic
from events.models import TopicCategory


class Command(BaseCommand):
    help = "Create initial topics based on TopicCategory"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating topics...")
        for category in TopicCategory.choices:
            Topic.objects.get_or_create(name=category[0])
        self.stdout.write(self.style.SUCCESS("Topics created successfully!"))
