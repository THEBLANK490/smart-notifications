from django.urls import path

from apps.notifications.api.views.in_app_notifications import MarkAsReadAPIView, NotificationHistoryAPIView, UnreadNotificationsAPIView
from apps.notifications.api.views.thread_views import ThreadGetView, ThreadSubscriptionView, ThreadView
from apps.notifications.api.views.trigger_views import CommentView
from apps.notifications.api.views.notification_preference_view import NotificationPreferencesView

app_name = "notifications"

urlpatterns = [
    path("notification-preferences/<int:user_id>/",NotificationPreferencesView.as_view(),name="notification-preference-change"),
    path("trigger/",CommentView.as_view(),name="comment-post"),
    path("thread/create/",ThreadView.as_view(),name="thread-create"),
    path("thread/fetch/",ThreadGetView.as_view(),name="thread-fetch"),
    path("thread-subscription/create/",ThreadSubscriptionView.as_view(),name="thread-subscription-create"),
    path('notifications/unread/', UnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications/read/', MarkAsReadAPIView.as_view(), name='mark-read'),
    path('notifications/history/', NotificationHistoryAPIView.as_view(), name='notification-history'),
]