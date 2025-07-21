from celery import shared_task

from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.notifications.models import Notification

@shared_task
def send_weekly_summary() -> None:
    """
    Celery task to send a weekly summary of unread notifications to users.

    This task performs the following:
    - Iterates over all users.
    - Fetches unread notifications created within the last 7 days.
    - If such notifications exist, creates a new in-app notification
      summarizing the count of unread items.

    Returns:
        None
    """
    User = get_user_model()
    users = User.objects.all()

    for user in users:
        last_week = timezone.now() - timezone.timedelta(days=7)
        recent_notifications = Notification.objects.filter(
            recipient=user,
            created_at__gte=last_week,
            is_read=False
        )

        if recent_notifications.exists():
            message = f"You have {recent_notifications.count()} unread notifications from this week."

            Notification.objects.create(
                recipient=user,
                message=message,
                in_app_status=True,
                email_status=False,
                sms_status=False,
                is_read=False
            )
