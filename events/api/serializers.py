from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from events.models import Company, CompanySocialMedia


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
