from rest_framework import exceptions
from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    media_type = "application/json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        keys = ["data", "message", "errors"]
        if not "data" in data:  # noqa
            data.update({"data": {}})
        if not "errors" in data:  # noqa
            data.update({"errors": []})
        if not sorted(keys) == sorted(list(data.keys())):
            raise exceptions.ValidationError(
                {"message": "Cannot find all keys on payload"}
            )
        return super().render(data, accepted_media_type, renderer_context)