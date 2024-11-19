from django.urls import path

from events.api.views import (
    CompanyViewSet,
    EventViewSet,
    EventRegistrationListView,
    EventRegistrationCreateView,
    EventRegistrationUpdateView,
)

urlpatterns = [
    path("", EventViewSet.as_view({"get": "list"}), name="event_list"),
    path("create/", EventViewSet.as_view({"post": "create"}), name="event_create"),
    path(
        "<str:id>/",
        EventViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="event_detail",
    ),
    path("companies/list/", CompanyViewSet.as_view({"get": "list"}), name="companies_list"),
    path("companies/create/", CompanyViewSet.as_view({"post": "create"}), name="company_create"),
    path(
        "companies/<slug:slug>/",
        CompanyViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="company_detail",
    ),
    path("registrations/list/", EventRegistrationListView.as_view(), name="event_registrations_list"),
    path("registrations/create/", EventRegistrationCreateView.as_view(), name="event_registrations_create"),
    path("registrations/<str:id>/update/", EventRegistrationUpdateView.as_view(), name="event_registration_update"),
]
