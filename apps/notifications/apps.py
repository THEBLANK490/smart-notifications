from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'

    def ready(self):
        from .signals import handle_new_comment # noqa: F821
        from django.db.models.signals import post_save
        from apps.notifications.models import Comment
        
        post_save.connect(handle_new_comment, sender=Comment)
