from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, KnownDevice


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("id",)
    list_display = ("id", "email", "mobile", "is_active", "is_staff", "first_login", "last_login")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "mobile")
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "mobile")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Other Info"), {"fields": ("first_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "mobile", "password1", "password2"),
        }),
    )


@admin.register(KnownDevice)
class KnownDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "device_fingerprint", "ip_address", "last_used")
    list_filter = ("last_used", "user")
    search_fields = ("user__email", "ip_address", "device_fingerprint", "user_agent")
    readonly_fields = ("last_used",)
