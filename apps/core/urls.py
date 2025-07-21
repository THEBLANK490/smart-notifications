from django.urls import include, path

app_name = "core"
urlpatterns = [
    path("user/", include("apps.accounts.api.urls"), name="user"),
    path("notifications/", include("apps.notifications.api.urls"), name="notifications"),
]
