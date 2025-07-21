import logging
from celery import shared_task

from apps.notifications.notifications_tasks import send_email_notification, send_sms_notification
from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationPreference

logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=60,
    max_retries=3,
    time_limit=30
)
def handle_unknown_device_async(user_id, device_info):
    try:
        user = User.objects.get(id=user_id)
        pref = NotificationPreference.objects.filter(user=user).first()
            
        message = "Unknown device login detected"
        
        notification = Notification.objects.create(
            recipient=user,
            message=message,
            in_app_status=pref.in_app,
            is_read=False
        )
        if pref.email:
            send_email_notification.delay(
                notification.id,
                "Unknown Device Detected",
                message
            )
            
        if pref.sms:
            send_sms_notification.delay(
                notification.id,
                message[:160]
            )
            
        notification.message = f"{message}\n\nDevice Info:\nIP: {device_info['ip']}\nUser Agent: {device_info['user_agent']}"
        notification.save(update_fields=['message'])
        
    except User.DoesNotExist:
        logger.error(f"User not found for unknown device notification: {user_id}")