from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.serializers import CreateAccountSerializer, CreateOrganizerSerializer

User = get_user_model()


class CreateAccountView(APIView):
    """
    API view for creating a new user account with an associated Participant profile.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "User profile created successfully.",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CreateOrganizerView(CreateAPIView):
    """
    API view for creating an Organizer profile.
    Restricted to superadmins only.
    """

    serializer_class = CreateOrganizerSerializer
    permission_classes = [IsAdminUser]
