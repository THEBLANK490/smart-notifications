import logging 

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle,AnonRateThrottle

from apps.accounts.api.serializers import LoginSerializer, UserRegisterSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, inline_serializer

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    """
    API view to handle user registration.
    Allows a new user to register by providing required fields like email and password.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = []
    throttle_classes = [AnonRateThrottle] 

    @extend_schema(
        operation_id="User Registration ApI.",
        summary="SN-UR-01",
        description="""
        An Api to register an user.
        """,
        request=UserRegisterSerializer,
        tags=["Users",],
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                "success_user_create_response",
                fields={
                    "message": serializers.CharField(
                        default="User created successfully."
                    ),
                    "data": UserRegisterSerializer(),
                },
            ),
            status.HTTP_400_BAD_REQUEST: inline_serializer(
                "error_400_response",
                fields={
                    "message": serializers.CharField(default="Invalid data."),
                    "errors": serializers.ListField(
                        child=serializers.DictField(),
                        default=[{"email": "This field is required."}],
                    ),
                },
            ),
            status.HTTP_403_FORBIDDEN: inline_serializer(
                "error_403_response_while_registering",
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
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user registration.

        Args:
            request (Request): HTTP request object containing user registration data.

        Returns:
            Response: JSON response with success or error message.
        """
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("New user registered successfully with email: %s", serializer.data.get("email"))
        return Response(
            {
                "message": "User Registration Successful!",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

class UserLoginView(APIView):
    """
    API view to handle user login.
    Validates credentials and returns JWT tokens and user info.
    """
    
    permission_classes = []
    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    @extend_schema(
        operation_id="user_login",
        summary="SN-UR-02",
        description="Returns JWT tokens and user info on valid credentials.",
        tags=["Users"],
        request=serializer_class,
        responses={
            200: inline_serializer(
                name="LoginSuccessResponse",
                fields={
                    "refresh": serializers.CharField(),
                    "access": serializers.CharField(),
                    "user": serializers.DictField(),
                }
            ),
            400: inline_serializer(
                name="LoginErrorResponse",
                fields={
                    "message": serializers.CharField(default="Invalid credentials."),
                    "errors": serializers.ListField(
                        child=serializers.DictField(),
                        default=[{"email": "Invalid or required."}]
                    )
                }
            )
        },
    )
    def post(self, request):
        """
        Handle POST request for user login.

        Args:
            request (Request): HTTP request object containing login credentials.

        Returns:
            Response: JSON response with JWT tokens and user information or error.
        """
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("User login successful: %s", serializer.validated_data["user"].email)
        return Response(
            {
                "message": "User Login Successful!",
                "data": {
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                    "user": UserSerializer(serializer.validated_data["user"]).data
                }
            },
            status=status.HTTP_200_OK,
        )