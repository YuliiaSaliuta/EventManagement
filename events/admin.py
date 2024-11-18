from django import forms
from django.contrib import admin

from events.models import Topic, CompanySocialMedia, Company, EventSocialMedia, Event


class CompanySocialMediaInline(admin.TabularInline):
    """
    Inline model for Company Social Media.
    """

    model = CompanySocialMedia
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin model for Company.
    """

    list_display = ("name", "website_url")
    search_fields = ("name",)
    inlines = [CompanySocialMediaInline]


@admin.register(CompanySocialMedia)
class CompanySocialMediaAdmin(admin.ModelAdmin):
    """
    Admin model for Company Social Media.
    """

    list_display = ("company", "platform", "url")
    search_fields = ("company__name", "platform")
    list_filter = ("platform", "company")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Admin model for Topic.
    """

    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class EventSocialMediaInline(admin.TabularInline):
    """
    Inline model for Event Social Media.
    """

    model = EventSocialMedia
    extra = 0


class EventForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Event
        fields = "__all__"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin model for Event.
    """

    form = EventForm

    list_display = ("title", "event_start_date", "event_start_time", "status")
    search_fields = ("title", "description", "organizer__user__email", "company__name")
    list_filter = ("status", "event_start_date", "event_start_time", "city", "country")
    inlines = [EventSocialMediaInline]


@admin.register(EventSocialMedia)
class EventSocialMediaAdmin(admin.ModelAdmin):
    """
    Admin model for Event Social Media.
    """

    list_display = ("event", "platform", "url")
    search_fields = ("event__title", "platform")
    list_filter = ("platform", "event")
