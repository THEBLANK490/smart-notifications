import logging 

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle


from drf_spectacular.utils import extend_schema, inline_serializer

from apps.accounts.models import User
from apps.core.utils import get_or_not_found
from apps.notifications.api.serializers import NotificationPreferenceSerailizer
from apps.notifications.models import NotificationPreference

logger = logging.getLogger(__name__)

class NotificationPreferencesView(APIView):
    """
    API view to retrieve and update a user's notification preferences.
    """
    serializer_class = NotificationPreferenceSerailizer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    def get_throttles(self):
        if self.request.method == 'GET':
            self.throttle_scope = 'notification_pref_get'
        elif self.request.method == 'PATCH':
            self.throttle_scope = 'notification_pref_patch'
        return super().get_throttles()
    
    def get_queryset(self, user):
        """
        Retrieve the NotificationPreference object for the given user ID.

        Args:
            user (int): User ID from URL.

        Returns:
            NotificationPreference: Related notification preference object.

        Raises:
            Http404: If the user does not exist.
        """
        user = get_or_not_found(User.objects.all(),id=user)
        return NotificationPreference.objects.filter(user=user).first()
        

    @extend_schema(
        operation_id="Notification Preferences Change Api.",
        summary="SN-NP-01",
        description="""
        An Api to update notification preference.
        """,
        request=serializer_class,
        tags=["Notification Preferences",],
        responses={
            status.HTTP_200_OK: inline_serializer(
                "success_notification_preferences_update_response",
                fields={
                    "message": serializers.CharField(
                        default="Notification Preferences updated successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
            status.HTTP_404_NOT_FOUND: inline_serializer(
                "error_404_response",
                fields={
                    "message": serializers.CharField(default="NotificationPreference instance not found."),
                    "errors": serializers.ListField(
                        child=serializers.DictField(),
                        default=[],
                    ),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response_in_notification_prererence",
                fields={
                    "message": serializers.CharField(default="Permission Denied."),
                    "errors": serializers.ListField(
                        child=serializers.DictField(),
                        default=[
                            {
                                "message": [
                                    "You do not have permission to perform this action."
                                ]
                            }
                        ],
                    ),
                },
            ),
        },
    )    
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH request to update notification preferences for a user.

        Args:
            request: HTTP request containing updated preference data.
            kwargs: Contains `user_id` used to fetch user.

        Returns:
            Response: Success response with updated data.

        Notes:
            - Uses partial update
            - Responds with 200 on success
        """
        instance = self.get_queryset(user=kwargs.get("user_id"))
        serializer = self.serializer_class(
            instance=instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Notification preferences updated for user ID: %s", kwargs.get("user_id"))
        return Response(
            {
                "message": "Notification Preference Updated Successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    @extend_schema(
        operation_id="Notification Preference get Api.",
        summary="SN-NP-02",
        description="""
        An Api to get Notification Preferences of a user.
        """,
        request=serializer_class,
        tags=["Notification Preferences",],
        responses={
            status.HTTP_200_OK: inline_serializer(
                "success_notification_preference_fetch_response",
                fields={
                    "message": serializers.CharField(
                        default="Notification Preferences fetched successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
        },
    )
    def get(self,request,*args,**kwargs):
        """
        Handle GET request to retrieve a user's notification preferences.

        Args:
            request: HTTP request.
            kwargs: Contains `user_id`.

        Returns:
            Response: User’s notification preferences.
        """
        queryset = self.get_queryset(user=kwargs.get("user_id"))
        serializer = self.serializer_class(queryset)
        logger.info("Notification preferences retrieved for user ID: %s", kwargs.get("user_id"))
        return Response(
            {
                "message": "Notification Preferences Fetched Successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
