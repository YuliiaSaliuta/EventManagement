from django.urls import path

from events.api.views import CompanyViewSet, EventViewSet

urlpatterns = [
    path("", EventViewSet.as_view({"get": "list"}), name="event_list"),
    path("create/", EventViewSet.as_view({"post": "create"}), name="event_create"),
    path(
        "<slug:slug>/",
        EventViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="event_detail",
    ),
    path("companies/", CompanyViewSet.as_view({"get": "list"}), name="companies_list"),
    path("companies/create/", CompanyViewSet.as_view({"post": "create"}), name="company_create"),
    path(
        "companies/<slug:slug>/",
        CompanyViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="company_detail",
    ),
]
