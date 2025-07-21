from apps.notifications.notifications_tasks import send_email_notification, send_sms_notification
from .models import Notification, NotificationPreference
from apps.notifications.models import ThreadSubscription,Comment

def dispatch_comment_notification(comment: Comment) -> None:
    """
    Dispatch notifications for a new comment on a thread.

    Args:
        comment (Comment): The comment instance that triggered the notification.

    Process:
        - Finds all thread subscribers excluding the comment author.
        - Checks their notification preferences.
        - Creates Notification objects accordingly.
        - Triggers asynchronous email and SMS notification tasks.
        - Updates Notification records with Celery task IDs.

    Notes:
        - Notifications are created in bulk for efficiency.
        - Email and SMS tasks are queued only if user preferences allow.
    """
    thread = comment.thread
    
    subscriptions = ThreadSubscription.objects.filter(
        thread=thread
    ).exclude(user=comment.user).select_related('user')
    
    user_ids = [sub.user_id for sub in subscriptions]
    preferences = NotificationPreference.objects.filter(
        user_id__in=user_ids
    ).in_bulk(field_name='user_id')
    
    notifications = []
    email_tasks = []
    sms_tasks = []
    
    for subscription in subscriptions:
        user = subscription.user
        pref = preferences.get(user.id)
        
        if not pref:
            continue
            
        message = f"New comment on '{thread.title}' by {comment.user.email}"
        subject = "New Comment Posted"
        
        notification = Notification(
            recipient=user,
            comment=comment,
            message=message,
            in_app_status=pref.in_app,
            is_read=False
        )
        
        if pref.email:
            notification.email_status = False
            notification.email_task_id = "pending"
        else:
            notification.email_status = False
            
        if pref.sms:
            notification.sms_status = False
            notification.sms_task_id = "pending"
        else:
            notification.sms_status = False
            
        notifications.append(notification)
    
    created_notifications = Notification.objects.bulk_create(notifications)
    
    for notification in created_notifications:
        if notification.email_task_id == "pending":
            task = send_email_notification.delay(notification.id,subject,message)
            notification.email_task_id = task.id
            email_tasks.append(notification.id)
            
        if notification.sms_task_id == "pending":
            task = send_sms_notification.delay(notification.id,message)
            notification.sms_task_id = task.id
            sms_tasks.append(notification.id)
    
    if email_tasks:
        Notification.objects.filter(id__in=email_tasks).update(
            email_task_id=send_email_notification.AsyncResult(email_tasks[0]).task_id
        )
        
    if sms_tasks:
        Notification.objects.filter(id__in=sms_tasks).update(
            sms_task_id=send_sms_notification.AsyncResult(sms_tasks[0]).task_id
        )
        
