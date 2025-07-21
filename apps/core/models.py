from django.db import models

class TimeStampAbstractModel(models.Model):
    """
    Inherit from this class to add timestamp fields in the model class.
    This model stores the datetime in reference to system timezone set value.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    """datetime: date on which the instance is created."""
    updated_at = models.DateTimeField(auto_now=True)
    """datetime: date on which the instance is updated."""

    class Meta:
        abstract = True


class UserCreatedUpdatedBy(TimeStampAbstractModel):
    """Inherit from this class to add created_by and updated_by fields in the model class"""

    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )
    """Foreign key to user who created the model instance."""
    updated_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated_by",
    )
    """Foreign key to user who updated the model instance."""

    class Meta:
        abstract = True
