from rest_framework import exceptions

def get_or_not_found(qs, **kwargs):
    """
    Retrieve an object from the queryset or raise a 404 Not Found exception.

    Args:
        qs (QuerySet): A Django queryset from which to retrieve an object
        **kwargs: The filters to apply when querying the queryset

    Returns:
        Model: The retrieved object from the queryset

    Raises:
        exceptions.NotFound: If the object is not found in the queryset
    """

    try:
        return qs.get(**kwargs)
    except qs.model.DoesNotExist:
        raise exceptions.NotFound(f"{qs.model.__name__} instance not found.")