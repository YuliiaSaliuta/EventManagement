from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.api import views

urlpatterns = [
    path("sign-up/", views.CreateAccountView.as_view(), name="create_account"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("organizers/create/", views.CreateOrganizerView.as_view(), name="create_organizer"),
]
