import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from events.models import Topic
from users.models import Participant, Organizer

User = get_user_model()


class CreateUserSerializer(ModelSerializer):
    """
    Serializer for creating a user only.
    """

    password = CharField(write_only=True, required=True)
    confirm_password = CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password", "first_name", "last_name", "phone", "avatar"]

    def validate(self, attrs):
        """
        Validate that the passwords match and comply with password policies.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError({"password": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create_user(self, validated_data):
        """
        Create and return a new User instance.
        """
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data["phone"],
            avatar=validated_data.get("avatar"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
        )


class CreateAccountSerializer(CreateUserSerializer):
    """
    Serializer for creating a user and associated Participant account.
    """

    interests = PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = CreateUserSerializer.Meta.fields + ["interests"]

    def create(self, validated_data):
        """
        Create a Participant account associated with the user.
        """
        user = self.create_user(validated_data)
        interests = validated_data.pop("interests", [])
        participant = Participant.objects.create(user=user)
        participant.interests.set(interests)
        participant.save()
        return user


class CreateOrganizerSerializer(CreateUserSerializer):
    """
    Serializer for creating a user and associated Organizer account.
    """

    bio = CharField(required=False, allow_blank=True)
    city = CharField(required=False, allow_blank=True)
    country = CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "avatar", "bio", "city", "country"]

    def validate(self, attrs):
        """
        Add custom validations for organizer creation if needed.
        """
        return attrs

    def create(self, validated_data):
        """
        Create an Organizer account associated with the user.
        """
        random_password = secrets.token_urlsafe(10)
        print(random_password)
        user = self.create_user({**validated_data, "password": random_password})
        # TODO: Implement email notification logic to send credentials to the user
        Organizer.objects.create(
            user=user,
            bio=validated_data.get("bio"),
            city=validated_data.get("city"),
            country=validated_data.get("country"),
        )
        return user
