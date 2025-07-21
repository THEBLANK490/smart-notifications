from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.notifications.models import Comment

@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance: Comment, created: bool, **kwargs) -> None:
    """
    Signal handler to trigger notification dispatch when a new Comment is created.

    Args:
        sender: The model class (Comment).
        instance: The Comment instance saved.
        created: Boolean indicating if this was a new creation.
        **kwargs: Additional keyword arguments.

    Process:
        - When a new comment is created, calls dispatch_comment_notification to send notifications.
    """
    if created:
        from .services import dispatch_comment_notification # noqa: F821
        dispatch_comment_notification(instance)