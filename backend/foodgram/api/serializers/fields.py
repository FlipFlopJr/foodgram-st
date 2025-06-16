from rest_framework import serializers
from django.core.files.base import ContentFile

import base64


class Base64Field(serializers.ImageField):
    def to_internal_value(self, data):
        if data.startswith("data:image") and isinstance(data, str):
            if data.startswith("data:image"):
                format, imgstr = data.split(";base64,")
                ext = format.split("/")[-1]
                data = ContentFile(
                    base64.b64decode(imgstr), name="temp." + ext
                )

        return super().to_internal_value(data)
