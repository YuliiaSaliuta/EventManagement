from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from events.api.serializers import CompanySerializer
from events.models import Company
from utils import permissions


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Company, including nested social media creation.
    """

    queryset = Company.objects.prefetch_related("social_media").all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, permissions.IsOrganizerOrAdminUserOrReadOnly]
    lookup_field = "slug"
