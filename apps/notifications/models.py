from django.db import models

from apps.accounts.models import User
from apps.core.models import UserCreatedUpdatedBy

class Thread(UserCreatedUpdatedBy):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "thread"


class Comment(UserCreatedUpdatedBy):
    content = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.user} on {self.thread}"

    class Meta:
        db_table = "comment"


class ThreadSubscription(UserCreatedUpdatedBy):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='subscriptions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        unique_together = ('thread', 'user')
        db_table = "thread_subscription"


class NotificationPreference(UserCreatedUpdatedBy):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    def __str__(self):
        return f"Preferences for {self.user}"
    
    class Meta:
        db_table = "notification_preference"


class Notification(UserCreatedUpdatedBy):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications',blank=True,null=True)
    in_app_status = models.BooleanField(default=False)
    email_status = models.BooleanField(default=False)
    sms_status = models.BooleanField(default=False)
    is_read=models.BooleanField(default=False)
    message = models.TextField()
    
    #storing the celery task id to update email and sms status after the celery tasks completes
    email_task_id = models.CharField(max_length=255, blank=True, null=True)
    sms_task_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.channel} notification to {self.recipient}"

    class Meta:
        db_table = "notification"