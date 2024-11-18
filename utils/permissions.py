from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizerOrAdminUserOrReadOnly(BasePermission):
    """
    Permission class that allows access if:
    - The request is a safe method (GET, HEAD, OPTIONS).
    - The user is an admin.
    - The user is the organizer associated with the event.
    """

    def has_permission(self, request, view):
        # Allow safe methods for any user
        if request.method in SAFE_METHODS:
            return True

        # Allow if the user is an admin
        if request.user and request.user.is_staff:
            return True

        # Allow if the user is the organizer
        if request.user and request.user.is_organizer():
            return True
        return False


class IsOrganizerOrAdminUser(BasePermission):
    """
    Permission class that allows access if:
    - The user is an admin.
    - The user is the organizer associated with the event.
    """
    def has_permission(self, request, view):
        # Allow if the user is an admin
        if request.user and request.user.is_staff:
            return True

        # Allow if the user is the organizer
        if request.user and request.user.is_organizer():
            return True
        return False


class IsParticipantOrAdminUser(BasePermission):
    """
    Permission class that allows access if:
    - The user is an admin.
    - The user is the participant associated with the event.
    """
    def has_permission(self, request, view):
        # Allow if the user is an admin
        if request.user and request.user.is_staff:
            return True

        # Allow if the user is the participant
        if request.user and request.user.is_participant():
            return True
        return False