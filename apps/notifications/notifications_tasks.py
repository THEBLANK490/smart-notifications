import logging

from celery import shared_task

from apps.accounts.models import User
from .models import Notification

logger = logging.getLogger(__name__)

def send_mock_email(user: User, subject: str, message: str) -> bool:
    """
    Simulate sending an email notification to a user.

    Args:
        user: User instance to whom the email will be sent.
        subject: Subject line of the email.
        message: Body content of the email.

    Returns:
        bool: True if sending succeeded, False otherwise.

    Logs:
        Info on sending attempt and errors if any.
    """
    try:
        logger.info(f"Mock email to {user.email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email failed to {user.email}: {str(e)}")
        return False

def send_mock_sms(user: User, message: str) -> bool:
    """
    Simulate sending an SMS notification to a user.

    Args:
        user: User instance to whom the SMS will be sent.
        message: SMS content (typically limited to 160 chars).

    Returns:
        bool: True if sending succeeded, False otherwise.

    Logs:
        Info on sending attempt and errors if any.
    """
    try:
        logger.info(f"Mock SMS to {user.email}: {message}")
        return True
    except Exception as e:
        logger.error(f"SMS failed to {user.email}: {str(e)}")
        return False
    
@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=60,
    max_retries=3,
    time_limit=30
)
def send_email_notification(notification_id: int, subject: str, message: str) -> None:
    """
    Celery task to send an email notification asynchronously.

    Args:
        notification_id: Primary key of the Notification object.
        subject: Email subject.
        message: Email message content.

    Side Effects:
        Updates the email_status and clears email_task_id on the Notification object.

    Retries:
        Retries up to 3 times with exponential backoff on exceptions.
    """
    notification = Notification.objects.get(id=notification_id)
    success = send_mock_email(
        notification.recipient,
        subject,
        message
    )
    notification.email_status = success
    notification.email_task_id = None
    notification.save(update_fields=['email_status', 'email_task_id'])
    

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=60,
    max_retries=3,
    time_limit=30
)
def send_sms_notification(notification_id: int, message: str) -> None:
    """
    Celery task to send an SMS notification asynchronously.

    Args:
        notification_id: Primary key of the Notification object.
        message: SMS message content (typically truncated to 160 characters).

    Side Effects:
        Updates the sms_status and clears sms_task_id on the Notification object.

    Retries:
        Retries up to 3 times with exponential backoff on exceptions.
    """
    notification = Notification.objects.get(id=notification_id)
    success = send_mock_sms(
        notification.recipient,
        message[:160]
    )
    notification.sms_status = success
    notification.sms_task_id = None
    notification.save(update_fields=['sms_status', 'sms_task_id'])