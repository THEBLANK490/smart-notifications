import logging

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle


from drf_spectacular.utils import extend_schema, inline_serializer

from apps.notifications.api.serializers import ThreadSerializer, ThreadSubscriptionSerializer
from apps.notifications.models import Thread

logger = logging.getLogger(__name__)

class ThreadView(APIView):
    """
    API endpoint to create a new discussion thread.
    """
    
    serializer_class= ThreadSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    def get_queryset(self):
        return Thread.objects.all()
    
    @extend_schema(
        operation_id="thread Post Api.",
        summary="SN-TH-01",
        description="""
        An Api to create threads.
        """,
        request=serializer_class,
        tags=["Thread",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_thread_create_response",
                fields={
                    "message": serializers.CharField(
                        default="Thread created successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response_in_thread",
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
    def post(self,request,*args,**kwargs):
        """
        Handle creation of new thread and auto-subscription.

        Args:
            request: HTTP request containing thread data.

        Returns:
            Response with created thread data and message.

        Notes:
            - The creating user is auto-subscribed to the thread.
        """
        serializer = self.serializer_class(data = request.data,context={"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Thread created successfully by user {request.user.id}.")
        return Response(
            {
                "message": "Threads Created Successful",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

class ThreadGetView(APIView):
    """
    API endpoint to retrieve all discussion threads.
    """
    
    serializer_class= ThreadSerializer
    permission_classes = []
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    def get_queryset(self):
        """
        A method to retrieve all threads.
        """
        return Thread.objects.all()
    
    @extend_schema(
        operation_id="thread get Api.",
        summary="SN-TH-02",
        description="""
        An Api to get all threads.
        """,
        request=serializer_class,
        tags=["Thread",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_thread_fetch_response",
                fields={
                    "message": serializers.CharField(
                        default="Thread fetched successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
        },
    )
    def get(self,request,*args,**kwargs):
        """
        Retrieve all discussion threads.

        Args:
            request: HTTP request.

        Returns:
            Response with serialized thread list.
        """
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset,many=True)
        logger.info(f"Fetched {len(serializer.data)} threads.")
        return Response(
            {
                "message": "Threads Fetched Successful",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
          
class ThreadSubscriptionView(APIView):
    """
    API endpoint to allow users to subscribe to a thread.
    """
    
    serializer_class= ThreadSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    @extend_schema(
        operation_id="thread subscription Post Api.",
        summary="SN-TH-01",
        description="""
        An Api to create threads subscription.
        """,
        request=serializer_class,
        tags=["Thread Subscription",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_thread_subscription_create_response",
                fields={
                    "message": serializers.CharField(
                        default="Thread Subscription created successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response_in_thread_subscription",
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
    def post(self,request,*args,**kwargs):
        """
        Subscribe the authenticated user to a thread.

        Args:
            request: HTTP request with thread ID.

        Returns:
            Response with subscription confirmation.

        Notes:
            - Prevents duplicate subscriptions.
        """
        serializer = self.serializer_class(data = request.data,context={"user":request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"User {request.user.id} subscribed to thread successfully.")
        return Response(
            {
                "message": "Threads Subscription Created Successful",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )