from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import localtime

from events.models import Event


@shared_task
def send_registration_email(user_email, registration_details):
    """
    Sends an email with the user's registration details.
    """
    subject = "Registration Details"

    event = Event.objects.get(id=registration_details.get("event"))
    status = registration_details.get("status")
    created_at = datetime.fromisoformat(registration_details.get("created_at"))
    updated_at = datetime.fromisoformat(registration_details.get("updated_at"))
    created_at = localtime(created_at)
    updated_at = localtime(updated_at)

    message = f"""
        Dear Participant,

        Thank you for registering for the event. Below are your registration details:

        Registration ID: {registration_details.get("id")}
        Status: {status}

        Event Information:
        - Title: {event.title}
        - Location: {event.location}
        - Start Date: {event.event_start_date.strftime('%d.%m.%Y')}
        - Start Time: {event.event_start_time.strftime('%H:%M')}
        - Organizer: {event.organizer.user.first_name} {event.organizer.user.last_name}

        Registration Timestamps:
        - Created At: {created_at.strftime('%d.%m.%Y %H:%M')}
        - Updated At: {updated_at.strftime('%d.%m.%Y %H:%M')}

        We are looking forward to your participation!

        Best regards,
        Event Management Team
        """
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
    )


@shared_task
def send_organizer_credentials_email(email, password, first_name):
    """
    Sends an email with credentials to the newly created organizer.
    """
    subject = "Your Organizer Account Credentials"
    message = f"""
    Dear {first_name},

    Your organizer account has been created successfully. Below are your credentials:

    Email: {email}
    Password: {password}

    Please log in and change your password immediately for security purposes.

    Best regards,
    Event Management Team
    """
    from_email = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message.strip(),
        from_email,
        [email],
    )
