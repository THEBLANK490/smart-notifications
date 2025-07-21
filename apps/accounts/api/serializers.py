import re
import logging

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password as password_validator

from apps.accounts.models import KnownDevice, User
from apps.accounts.services import get_device_fingerprint
from apps.notifications.models import NotificationPreference
from apps.accounts.tasks import handle_unknown_device_async

logger = logging.getLogger(__name__)

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles validation and creation of new user accounts with:
    - Password strength validation
    - Mobile number format validation
    - Email uniqueness check
    - Password confirmation matching
    - Automatic notification preference creation
    
    Attributes:
        password: Password field (min 8 chars, write-only)
        confirm_password: Password confirmation field (min 8 chars, write-only)
        mobile: Mobile number field (min 10 chars)
    """
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    mobile = serializers.CharField(min_length=10)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "mobile",
            "password",
            "confirm_password",
        )
        
    def validate_mobile(self, value: str) -> str:
        """
        Validate mobile number format and uniqueness.
        
        Args:
            value: Mobile number to validate
            
        Returns:
            Validated mobile number
            
        Raises:
            ValidationError: For invalid format or duplicate number
        """
        if not re.fullmatch(r"98\d{8}", value):
            raise serializers.ValidationError("Mobile number must start with '98' and be exactly 10 digits.")
        if User.objects.filter(mobile = value).exists():
            raise serializers.ValidationError("Mobile Number already exists.")
        return value

    def validate_password(self, value: str) -> str:
        """
        Validate password strength using Django's password validators.
        
        Args:
            value: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: For weak passwords
        """
        try:
            password_validator(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value: str) -> str:
        """
        Validate email uniqueness.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: For duplicate emails
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User already exists.")
        return value

    def validate(self, data: dict) -> dict:
        """
        Validate password confirmation match.
        
        Args:
            data: Serializer data dictionary
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: When passwords don't match
        """
        confirm_password = data.pop("confirm_password")
        password = data.get("password")
        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": ["Password fields didn't match."]}
            )
        return data

    def create(self, validated_data: dict) -> User:
        """
        Create a new user account with hashed password and notification preferences.
        
        Args:
            validated_data: Validated user data
            
        Returns:
            Created User instance
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        NotificationPreference.objects.get_or_create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    
    Provides safe representation of user information for API responses.
    """
    class Meta:
        model = User
        fields = ['id','email', 'mobile','first_name','last_name']

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.
    
    Handles:
    - User authentication with email/password
    - JWT token generation
    - Device recognition
    - Unknown device notifications
    
    Attributes:
        email: User's email address
        password: User's password
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs: dict) -> dict:
        """
        Authenticate user and generate JWT tokens.
        
        Args:
            attrs: Input attributes (email, password)
            
        Returns:
            Attributes with added user and token information
            
        Raises:
            ValidationError: For invalid credentials
        """
        request = self.context.get("request")
        email = attrs["email"]
        password = attrs["password"]
        user = authenticate(request=request, email=email, password=password)
        
        if not user:
            raise serializers.ValidationError({"authorization": "Invalid email or password."})
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        attrs["user"] = user
        attrs["refresh"] = str(refresh)
        attrs["access"] = access_token
        
        return attrs

    def create(self, validated_data: dict) -> dict:
        """
        Handle device recognition and first login tracking.
        
        Args:
            validated_data: Validated data from authentication
            
        Returns:
            Validated data dictionary
            
        Notes:
            - Creates device fingerprint for recognition
            - Triggers unknown device notifications async
            - Updates first login status
        """
        request = self.context.get("request")
        user = validated_data["user"]
        device_info = {}
        
        with transaction.atomic():
            ip = request.META.get("REMOTE_ADDR", "")
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            fingerprint = get_device_fingerprint(ip, user_agent)
            
            device_info = {
                "ip": ip,
                "user_agent": user_agent,
                "fingerprint": fingerprint
            }
            
            _, created = KnownDevice.objects.get_or_create(
                user=user,
                device_fingerprint=fingerprint,
                defaults={
                    'ip_address': ip,
                    'user_agent': user_agent
                }
            )
            
        
        if created and not user.first_login:
            handle_unknown_device_async.delay(user.id, device_info)
        
        if user.first_login:
            user.first_login = False
            user.save(update_fields=["first_login"])
            
        return validated_data