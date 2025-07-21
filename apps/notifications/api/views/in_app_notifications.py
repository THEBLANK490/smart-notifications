import logging
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle


from drf_spectacular.utils import extend_schema, inline_serializer,OpenApiParameter

from apps.core.pagination import CustomPagination
from apps.notifications.api.serializers import MarkReadSerializer, NotificationSerializer
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)

class UnreadNotificationsAPIView(APIView):
    """
    API view to fetch unread notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'unread_notifications'
    
    def get_queryset(self,request):
        """
        Fetch unread notifications for the authenticated user.

        Args:
            request: HTTP request object.

        Returns:
            QuerySet of unread notifications.
        """
        return Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).select_related('comment', 'comment__thread', 'comment__user')
    
    @extend_schema(
        operation_id="Unread Notification fetch Api.",
        summary="SN-NF-01",
        description="""
        An Api to get Unread Notification of a user.
        """,
        request=serializer_class,
        tags=["Notification",],
        parameters=[
            OpenApiParameter(
                name="page",
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page_size",
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            status.HTTP_200_OK: inline_serializer(
                "success_unread_notification_fetch_response",
                fields={
                    "message": serializers.CharField(
                        default="Unread Notification fetched successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
        },
    )
    def get(self, request,*args,**kwargs):
        """
        Handle GET request to retrieve unread notifications.

        Args:
            request: HTTP request object.

        Returns:
            Response: List of unread notifications with pagination (if applicable).
        """
        queryset = self.get_queryset(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response =paginator.get_paginated_response(serializer.data)
            paginated_data = paginated_response.data
            logger.info("Unread notifications fetched for user %s", request.user.id)
            return Response(
                {
                    "message": "Unread Notification fetched successfully.",
                    "data": paginated_data,
                },
                status=status.HTTP_200_OK,
            )
        
        serializer = self.serializer_class(queryset, many=True)
        logger.info("Unread notifications (no pagination) fetched for user %s", request.user.id)
        return Response(
                {
                    "message": "Unread Notification fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

class MarkAsReadAPIView(APIView):
    """
    API view to mark specific notifications as read.
    """
    serializer_class = MarkReadSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'mark_notifications_read'
    
    @extend_schema(
        operation_id="mark notifications as read Post Api.",
        summary="SN-NF-02",
        description="""
        An api to mark notifications as read.
        """,
        request=serializer_class,
        tags=["Notification",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_read_status_changed_response",
                fields={
                    "message": serializers.CharField(
                        default="Notifications Marked as read."
                    ),
                    "data": serializer_class(),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response",
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
    def post(self, request,*args,**kwargs):
        """
        Handle POST request to mark notifications as read.

        Args:
            request: HTTP request with a list of notification IDs.

        Returns:
            Response: Confirmation message and count of notifications marked as read.
        """
        serializer = self.serializer_class(data=request.data,context={"user":request.user})
        serializer.is_valid(raise_exception=True)
        updated_count = serializer.save()
        logger.info(
            "User %s marked %d notifications as read.", request.user.id, updated_count
        )
        return Response(
                {
                    "message": "Notifications Marked as read.",
                    "data": {"marked_read": serializer.validated_data},
                },
                status=status.HTTP_200_OK,
            )


class NotificationHistoryAPIView(APIView):
    """
    API view to fetch all notifications for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'notification_history'
    
    def get_queryset(self,request):
        """
        Retrieve all notifications for the current user.

        Args:
            request: HTTP request object.

        Returns:
            QuerySet of all notifications.
        """
        return Notification.objects.filter(
            recipient=request.user
        ).select_related(
            'comment', 'comment__thread', 'comment__user'
        ).order_by('-created_at')
        
    
    @extend_schema(
        operation_id="Notification History fetch Api.",
        summary="SN-NF-03",
        description="""
        An Api to get all Notification of a user.
        """,
        request=serializer_class,
        tags=["Notification",],
        parameters=[
            OpenApiParameter(
                name="page",
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page_size",
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            status.HTTP_200_OK: inline_serializer(
                "success_all_notification_fetch_response",
                fields={
                    "message": serializers.CharField(
                        default="Notifications fetched successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
        },
    )
    def get(self, request,*args,**kwargs):        
        """
        Handle GET request to fetch all notifications.

        Args:
            request: HTTP request object.

        Returns:
            Response: All notifications with pagination (if applicable).
        """
        queryset = self.get_queryset(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response =paginator.get_paginated_response(serializer.data)
            paginated_data = paginated_response.data
            logger.info("Notification history fetched for user %s (paginated)", request.user.id)
            return Response(
                {
                    "message": "Notifications fetched successfully.",
                    "data": paginated_data,
                },
                status=status.HTTP_200_OK,
            )
        
        serializer = self.serializer_class(queryset, many=True)
        logger.info("Notification history fetched for user %s (no pagination)", request.user.id)
        return Response(
                {
                    "message": "Notifications fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
