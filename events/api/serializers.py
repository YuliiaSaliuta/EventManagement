from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from events.models import Topic, Company, CompanySocialMedia, EventSocialMedia, Event
from users.models import Organizer


class CompanySocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySocialMedia
        fields = ["platform", "url"]

    def create(self, validated_data):
        """
        Create a new `CompanySocialMedia` instance.
        """
        company = self.context.get("company")
        if not company:
            raise ValidationError("Company context is required for creating social media links.")
        try:
            return CompanySocialMedia.objects.create(company=company, **validated_data)
        except IntegrityError as e:
            raise ValidationError(
                {"detail": "Ensure that all provided social media platforms are unique.", "error": str(e)}
            )

    def update(self, instance, validated_data):
        """
        Update an existing `CompanySocialMedia` instance.
        """
        instance.url = validated_data.get("url", instance.url)
        instance.save()
        return instance


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for processing information about the company and its social networks
    """

    social_media = CompanySocialMediaSerializer(many=True, required=False)

    class Meta:
        model = Company
        fields = ["id", "name", "description", "website_url", "slug", "created_at", "updated_at", "social_media"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new `Company` instance and associated social media entries.
        """
        social_media_data = validated_data.pop("social_media", [])
        company = Company.objects.create(**validated_data)
        for social_media in social_media_data:
            serializer = CompanySocialMediaSerializer(data=social_media, context={"company": company})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return company

    def update(self, instance, validated_data):
        """
        Update an existing company instance with new data. If social media data is provided,
        it updates or creates new entries in the CompanySocialMedia model.
        """
        # Update company fields
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.website_url = validated_data.get("website_url", instance.website_url)
        instance.save()

        # Update existing social media instances
        social_media_data = validated_data.pop("social_media", [])
        existing_social_media = {sm.platform: sm for sm in instance.social_media.all()}
        updated_platforms = set()

        for social_media in social_media_data:
            platform = social_media.get("platform")
            if platform in existing_social_media:
                sm_instance = existing_social_media[platform]
                serializer = CompanySocialMediaSerializer(sm_instance, data=social_media)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated_platforms.add(platform)
            else:
                serializer = CompanySocialMediaSerializer(data=social_media, context={"company": instance})
                serializer.is_valid(raise_exception=True)
                serializer.save()

        for platform, sm_instance in existing_social_media.items():
            if platform not in updated_platforms:
                sm_instance.delete()

        return instance


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["name"]


class EventSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSocialMedia
        fields = ["platform", "url"]

    def create(self, validated_data):
        """
        Create a new `EventSocialMedia` instance.
        """
        event = self.context.get("event")
        if not event:
            raise ValidationError("Event context is required for creating social media links.")
        try:
            return EventSocialMedia.objects.create(event=event, **validated_data)
        except IntegrityError as e:
            raise ValidationError(
                {"detail": "Ensure that all provided social media platforms are unique.", "error": str(e)}
            )

    def update(self, instance, validated_data):
        """
        Update an existing `EventSocialMedia` instance.
        """
        instance.url = validated_data.get("url", instance.url)
        instance.save()
        return instance


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for processing information about the event and its social networks
    """

    social_media = CompanySocialMediaSerializer(many=True, required=False)
    topics = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "event_start_time",
            "event_end_time",
            "event_start_date",
            "event_end_date",
            "city",
            "country",
            "location",
            "capacity",
            "delivery_type",
            "status",
            "event_type",
            "topics",
            "company",
            "organizer",
            "image",
            "slug",
            "created_at",
            "updated_at",
            "social_media",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        """
        Modify the serializer fields dynamically based on the user's role.
        If the user is an organizer, make the 'organizer' field auto-filled with the logged-in user.
        """
        user = kwargs["context"]["request"].user
        if user.is_organizer():
            self.fields["organizer"].read_only = True
        super().__init__(*args, **kwargs)

    def validate(self, data):
        """
        Modify the 'organizer' field dynamically based on the user's role.
        If the user is an organizer, set the 'organizer' field to the logged-in user.
        """
        user = self.context["request"].user
        if user.is_organizer():
            try:
                organizer = Organizer.objects.get(user=user)
                data["organizer"] = organizer
            except Organizer.DoesNotExist:
                raise ValidationError("The current user is not associated with any organizer profile.")
        return data

    def create(self, validated_data):
        """
        Create a new `Event` instance and associated social media entries.
        """
        topics_data = validated_data.pop("topics", [])
        social_media_data = validated_data.pop("social_media", [])
        event = Event.objects.create(**validated_data)
        event.topics.set(topics_data)

        for social_media in social_media_data:
            serializer = EventSocialMediaSerializer(data=social_media, context={"event": event})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return event

    def update(self, instance, validated_data):
        """
        Update an existing `Event` instance with new data. If social media data is provided,
        it updates or creates new entries in the EventSocialMedia model.
        """
        # Update the fields of the Event instance
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.event_start_time = validated_data.get("event_start_time", instance.event_start_time)
        instance.event_end_time = validated_data.get("event_end_time", instance.event_end_time)
        instance.event_start_date = validated_data.get("event_start_date", instance.event_start_date)
        instance.event_end_date = validated_data.get("event_end_date", instance.event_end_date)
        instance.city = validated_data.get("city", instance.city)
        instance.country = validated_data.get("country", instance.country)
        instance.location = validated_data.get("location", instance.location)
        instance.capacity = validated_data.get("capacity", instance.capacity)
        instance.delivery_type = validated_data.get("delivery_type", instance.delivery_type)
        instance.status = validated_data.get("status", instance.status)
        instance.event_type = validated_data.get("event_type", instance.event_type)
        instance.image = validated_data.get("image", instance.image)
        instance.organizer = validated_data.get("organizer", instance.organizer)
        instance.save()

        # Update topics
        topics_data = validated_data.pop("topics", [])
        if topics_data:
            instance.topics.set(topics_data)

        # Update existing social media instances
        social_media_data = validated_data.pop("social_media", [])
        existing_social_media = {sm.platform: sm for sm in instance.social_media.all()}
        updated_platforms = set()

        for social_media in social_media_data:
            platform = social_media.get("platform")
            if platform in existing_social_media:
                sm_instance = existing_social_media[platform]
                serializer = EventSocialMediaSerializer(sm_instance, data=social_media)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated_platforms.add(platform)
            else:
                serializer = EventSocialMediaSerializer(data=social_media, context={"event": instance})
                serializer.is_valid(raise_exception=True)
                serializer.save()

        for platform, sm_instance in existing_social_media.items():
            if platform not in updated_platforms:
                sm_instance.delete()

        return instance
