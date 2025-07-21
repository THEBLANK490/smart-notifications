import logging

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle

from drf_spectacular.utils import extend_schema, inline_serializer

from apps.notifications.api.serializers import CommentSerializer

logger = logging.getLogger(__name__)

class CommentView(APIView):
    """
    API endpoint to allow authenticated users to create comments on threads.
    """
    
    serializer_class= CommentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    @extend_schema(
        operation_id="Comment Post Api.",
        summary="SN-CM-01",
        description="""
        An Api to create comments.
        """,
        request=serializer_class,
        tags=["Comment",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_comment_create_response",
                fields={
                    "message": serializers.CharField(
                        default="Comment created successfully."
                    ),
                    "data": serializer_class(),
                },
            ),
            status.HTTP_404_NOT_FOUND: inline_serializer(
                "error_404_response_in_comment",
                fields={
                    "message": serializers.CharField(default="Invalid data."),
                    "errors": serializers.ListField(
                        child=serializers.DictField(),
                        default=[{"user": "User not Found."}],
                    ),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response_in_comment",
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
        Create a new comment on a thread.

        Args:
            request: HTTP POST request containing comment data, including
                     the thread ID and comment content.

        Context:
            user: Injected into serializer context to associate comment with user.

        Returns:
            Response:
                - Success: Message and serialized comment data.
                - Failure: Validation errors or permission issues.

        Notes:
            - Automatically assigns the current user as the author of the comment.
            - Ensures the thread exists before saving.
        """
        serializer = self.serializer_class(data = request.data,context = {"user":request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        logger.info(f"Comment successfully created by user {request.user.id}.")
        return Response(
            {
                "message": "Comments Created Successful",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )



