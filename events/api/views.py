from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.api.serializers import CompanySerializer, EventSerializer, EventRegistrationSerializer
from events.models import Company, Event, EventRegistration
from users.models import Participant
from utils import permissions
from utils.choices import EventRegistrationStatus
from utils.permissions import IsOrganizerOrAdminUserOrReadOnly, IsOrganizerOrAdminUser, IsParticipantOrAdminUser


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Company, including nested social media creation.
    """

    queryset = Company.objects.prefetch_related("social_media").all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrAdminUserOrReadOnly]
    lookup_field = "slug"


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Event, including nested social media creation.
    """

    queryset = Event.objects.prefetch_related("social_media").all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrAdminUserOrReadOnly]
    lookup_field = "slug"


class EventRegistrationListView(ListAPIView):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer


# class EventRegistrationListView2(APIView):
#     """
#     View to list all the registrations based on user role.
#     """
#
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         """
#         Return all registrations for the current user.
#         """
#         user = request.user
#         print(user)
#
#         if user.is_superuser:
#             print("User is admin")
#             # Superuser can view all registrations
#             registrations = EventRegistration.objects.all()
#         elif user.is_participant():
#             print("User is participating")
#             # Participant can only see their own registrations
#             registrations = EventRegistration.objects.filter(participant__user=user)
#         elif user.is_organizer():
#             # Organizer can view registrations for events they organize
#             print("User is organizer")
#             events = Event.objects.filter(organizer__user=user)
#             registrations = EventRegistration.objects.filter(event__in=events)
#         else:
#             registrations = EventRegistration.objects.none()
#
#         serializer = EventRegistrationSerializer(registrations, many=True)
#         return Response(serializer.data)


class EventRegistrationCreateView(APIView):
    """
    View to create a registration for the logged-in participant or admin.
    """

    permission_classes = [IsAuthenticated, IsParticipantOrAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = EventRegistrationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
