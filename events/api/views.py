from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from events.api.serializers import CompanySerializer, EventSerializer
from events.models import Company, Event
from utils import permissions


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Company, including nested social media creation.
    """

    queryset = Company.objects.prefetch_related("social_media").all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, permissions.IsOrganizerOrAdminUserOrReadOnly]
    lookup_field = "slug"


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Event, including nested social media creation.
    """

    queryset = Event.objects.prefetch_related("social_media").all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, permissions.IsOrganizerOrAdminUserOrReadOnly]
    lookup_field = "slug"
