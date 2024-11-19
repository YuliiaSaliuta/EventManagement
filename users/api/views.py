from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.serializers import CreateAccountSerializer, CreateOrganizerSerializer

User = get_user_model()


@extend_schema(
    summary="Create a new user account",
    description=(
        "Registers a new user with the participant role. "
        "Upon successful registration, it returns JWT tokens (access and refresh) for authentication."
    ),
    request=CreateAccountSerializer,
    responses={
        201: "User created successfully with tokens returned.",
        400: "Validation error. Check the input fields.",
    },
)
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


@extend_schema(
    summary="Create an Organizer profile",
    description=(
        "Allows superadmins to create a new organizer profile. "
        "This endpoint is restricted to users with superadmin privileges."
    ),
    request=CreateOrganizerSerializer,
    responses={
        201: "Organizer profile created successfully.",
        400: "Validation error. Check the input fields.",
        403: "Access forbidden. Only superadmins can perform this action.",
    },
)
class CreateOrganizerView(CreateAPIView):
    """
    API view for creating an Organizer profile.
    Restricted to superadmins only.
    """

    serializer_class = CreateOrganizerSerializer
    permission_classes = [IsAdminUser]
