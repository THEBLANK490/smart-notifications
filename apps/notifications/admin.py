from django.contrib import admin
from apps.notifications.models import (
    Thread,
    Comment,
    ThreadSubscription,
    NotificationPreference,
    Notification
)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "created_at", "updated_by", "updated_at")
    list_filter = ("created_by", "created_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "thread", "short_content", "created_at")
    list_filter = ("user", "thread", "created_at")
    search_fields = ("content", "user__email", "thread__title")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Content"


@admin.register(ThreadSubscription)
class ThreadSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "thread", "created_at")
    list_filter = ("user", "thread")
    search_fields = ("user__email", "thread__title")
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "in_app", "email", "sms", "created_at")
    list_filter = ("in_app", "email", "sms")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "recipient", "message_snippet", "in_app_status", "email_status",
        "sms_status", "is_read", "created_at"
    )
    list_filter = ("in_app_status", "email_status", "sms_status", "is_read", "created_at")
    search_fields = ("recipient__email", "message", "comment__content")
    readonly_fields = (
        "created_at", "updated_at", "created_by", "updated_by", 
        "email_task_id", "sms_task_id"
    )

    def message_snippet(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_snippet.short_description = "Message"
