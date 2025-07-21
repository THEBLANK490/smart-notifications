from typing import Any, Dict

from rest_framework import serializers

from apps.notifications.models import Comment, Notification, NotificationPreference, Thread, ThreadSubscription


class NotificationPreferenceSerailizer(serializers.ModelSerializer):
    """
    Serializer for user's notification preferences.
    Includes in-app, email, and SMS preferences.
    """
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            "user",
            "in_app",
            "email",
            "sms"
        ]
    

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments in a thread.
    Automatically assigns the user from context.
    """
    created_at = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "content",
            "thread",
            "user",
            "created_at"
        ]
    
    def create(self, validated_data: Dict[str, Any]) -> Comment:
        """
        Create a new comment and assign it to the current user.

        Args:
            validated_data (dict): Validated data for comment creation.

        Returns:
            Comment: Newly created comment instance.
        """
        validated_data["user"] = self.context.get("user")
        return super().create(validated_data)

class ThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for creating threads.
    Automatically subscribes the creator to the thread.
    """
    
    class Meta:
        model = Thread
        fields = ['id','title']
        
    def create(self, validated_data: Dict[str, Any]) -> Thread:
        """
        Create a new thread and subscribe the creator to it.

        Args:
            validated_data (dict): Validated thread data.

        Returns:
            Thread: Newly created thread instance.

        Notes:
            - Automatically subscribes the creating user.
        """
        user = self.context.get("request").user
        thread = super().create(validated_data)
        ThreadSubscription.objects.get_or_create(thread=thread, user=user)
        return validated_data

class ThreadSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for subscribing a user to a thread.
    Prevents duplicate subscriptions.
    """
    
    class Meta:
        model = ThreadSubscription
        fields = ['thread']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure a user doesn't subscribe to the same thread multiple times.

        Args:
            attrs (dict): Validated subscription data.

        Returns:
            dict: Cleaned attributes.

        Raises:
            ValidationError: If subscription already exists.
        """
        if ThreadSubscription.objects.filter(thread = attrs.get("thread"),user=self.context.get("user")).exists():
            raise serializers.ValidationError({"Thread Subscription":"Thread Subscription already exists for this user."})
        return super().validate(attrs)
    
    def create(self, validated_data: Dict[str, Any]) -> ThreadSubscription:
        """
        Create a new thread subscription for the user.

        Args:
            validated_data (dict): Validated subscription data.

        Returns:
            ThreadSubscription: Created subscription instance.
        """
        validated_data['user'] = self.context.get('user')
        return super().create(validated_data)
    
class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications.
    Includes nested comment and thread data.
    """
    comment = CommentSerializer(allow_null=True)
    thread = ThreadSerializer(source='comment.thread', allow_null=True, read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'comment', 'thread', 'message', 'created_at', 'is_read',
            'in_app_status', 'email_status', 'sms_status'
        ]

class MarkReadSerializer(serializers.Serializer):
    """
    Serializer to mark multiple notifications as read.
    """
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_notification_ids(self, value: list[int]) -> list[int]:
        """
        Ensure provided notification IDs belong to the user.

        Args:
            value (list[int]): List of notification IDs.

        Returns:
            list[int]: Valid notification IDs.

        Raises:
            ValidationError: If any ID does not belong to the user.
        """

        user = self.context['user']
        valid_ids = set(
            Notification.objects.filter(
                recipient=user,
                id__in=value
            ).values_list('id', flat=True)
        )
        
        invalid_ids = set(value) - valid_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Notifications not found or not owned by you: {invalid_ids}"
            )
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> int:
        """
        Mark provided notifications as read.

        Args:
            validated_data (dict): Contains `notification_ids` list.

        Returns:
            int: Count of updated notification records.
        """
        notification_ids = validated_data['notification_ids']
        updated = Notification.objects.filter(
            id__in=notification_ids,
            recipient=self.context.get("user")
        ).update(is_read=True)
        return updated