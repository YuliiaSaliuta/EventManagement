from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.api.serializers import CompanySerializer, EventSerializer, EventRegistrationSerializer
from events.models import Company, Event, EventRegistration
from utils.permissions import (
    IsAdminOrReadOnly,
    IsEventOrganizerOrAdminUserOrReadOnly,
    IsOrganizerOrAdminUser,
    IsParticipantOrAdminUser,
)
from utils.tasks import send_registration_email


@extend_schema_view(
    list=extend_schema(
        summary="List all companies",
        description="Retrieve a list of all companies along with their social media details.",
        responses=CompanySerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific company",
        description="Get details of a specific company by its slug.",
        responses=CompanySerializer,
    ),
    create=extend_schema(
        summary="Create a company",
        description="Create a new company entry with social media details. Only admins can perform this action.",
        request=CompanySerializer,
        responses=CompanySerializer,
    ),
    update=extend_schema(
        summary="Update a company",
        description="Update the details of an existing company. Only admins can perform this action.",
        request=CompanySerializer,
        responses=CompanySerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update a company",
        description="Partially update the details of an existing company. Only admins can perform this action.",
        request=CompanySerializer,
        responses=CompanySerializer,
    ),
    destroy=extend_schema(
        summary="Delete a company",
        description="Delete an existing company by its slug. Only admins can perform this action.",
        responses=OpenApiResponse(description="Company deleted successfully."),
    ),
)
class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Company, including nested social media creation.
    """

    queryset = Company.objects.prefetch_related("social_media").all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    lookup_field = "slug"


@extend_schema_view(
    list=extend_schema(
        summary="List all events",
        description="Retrieve a list of all events, including their social media details and organizers.",
        responses=EventSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific event",
        description="Get details of a specific event by its ID.",
        responses=EventSerializer,
    ),
    create=extend_schema(
        summary="Create an event",
        description="Create a new event. Only authenticated organizers or admins can perform this action.",
        request=EventSerializer,
        responses=EventSerializer,
    ),
    update=extend_schema(
        summary="Update an event",
        description="Update the details of an existing event. Only the organizer or an admin can perform this action.",
        request=EventSerializer,
        responses=EventSerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update an event",
        description="Partially update the details of an existing event. Only the organizer or an admin can perform this action.",
        request=EventSerializer,
        responses=EventSerializer,
    ),
    destroy=extend_schema(
        summary="Delete an event",
        description="Delete an existing event by its ID. Only the organizer or an admin can perform this action.",
        responses=OpenApiResponse(description="Event deleted successfully."),
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Event, including nested social media creation.
    """

    queryset = Event.objects.prefetch_related("social_media").all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsEventOrganizerOrAdminUserOrReadOnly]
    lookup_field = "id"


@extend_schema(
    summary="List all event registrations",
    description="Returns a list of event registrations based on the user's role. Admins see all registrations, participants see their own, and organizers see registrations for their events.",
    responses=EventRegistrationSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter registrations by status (e.g., 'pending', 'approved').",
        )
    ],
)
class EventRegistrationListView(APIView):
    """
    View to list all the registrations based on user role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return all registrations for the current user.
        """
        user = request.user

        if user.is_superuser:
            # Superuser can view all registrations
            registrations = EventRegistration.objects.all()
        elif user.is_participant():
            # Participant can only see their own registrations
            registrations = EventRegistration.objects.filter(participant__user=user)
        elif user.is_organizer():
            # Organizer can view registrations for events they organize
            events = Event.objects.filter(organizer__user=user)
            registrations = EventRegistration.objects.filter(event__in=events)
        else:
            registrations = EventRegistration.objects.none()

        serializer = EventRegistrationSerializer(registrations, many=True, context={"request": request})
        return Response(serializer.data)


@extend_schema(
    summary="Create an event registration",
    description="Create a new registration for an event. Only participants or admins can perform this action.",
    request=EventRegistrationSerializer,
    responses=EventRegistrationSerializer,
)
class EventRegistrationCreateView(APIView):
    """
    View to create a registration for the logged-in participant or admin.
    """

    permission_classes = [IsAuthenticated, IsParticipantOrAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = EventRegistrationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        registration_details = serializer.data
        send_registration_email.delay(request.user.email, registration_details)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Update an event registration",
    description="Update the details of an existing event registration. Only the organizer or an admin can perform this action.",
    request=EventRegistrationSerializer,
    responses=EventRegistrationSerializer,
)
class EventRegistrationUpdateView(APIView):
    """
    View to update an existing event registration.
    """

    permission_classes = [IsAuthenticated, IsOrganizerOrAdminUser]

    def put(self, request, *args, **kwargs):
        registration_id = kwargs.get("id")
        try:
            registration = EventRegistration.objects.get(id=registration_id)
        except EventRegistration.DoesNotExist:
            raise ValidationError("Registration not found.")
        if request.user.is_organizer() and registration.event.organizer.user != request.user:
            return Response(
                {"detail": "You cannot modify registrations for this event."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = EventRegistrationSerializer(registration, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
