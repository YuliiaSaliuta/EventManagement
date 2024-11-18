from django.contrib import admin
from django import forms

from events.models import Topic
from users.models import User, Participant, Organizer, OrganizerSocialMedia


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin model for User.
    """

    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "phone")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("email",)


class ParticipantForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = Participant
        fields = "__all__"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """
    Admin model for Participant.
    """

    form = ParticipantForm

    list_display = (
        "user",
        "user__first_name",
        "user__last_name",
    )
    search_fields = ("user__email",)
    filter_horizontal = ("attended_events",)


class OrganizerSocialMediaInline(admin.TabularInline):
    """
    Inline model for Organizer Social Media.
    """

    model = OrganizerSocialMedia
    extra = 0


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    """
    Admin model for Organizer.
    """

    list_display = ("user", "user__first_name", "user__last_name", "city", "country")
    search_fields = ("user__email", "city", "country")
    inlines = [OrganizerSocialMediaInline]


@admin.register(OrganizerSocialMedia)
class OrganizerSocialMediaAdmin(admin.ModelAdmin):
    """
    Admin model for Organizer Social Media.
    """

    list_display = ("organizer", "platform", "url")
    search_fields = ("organizer__user__email", "platform")
    list_filter = ("platform", "organizer")
