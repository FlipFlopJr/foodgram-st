import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64Field(serializers.ImageField):
    """Поле для обработки изображений в формате base64"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            try:
                header, encoded = data.split(";base64,", 1)
                extension = header.split("/")[-1]
                decoded_file = base64.b64decode(encoded)
                data = ContentFile(decoded_file, name=f"temp.{extension}")
            except (ValueError, TypeError, IndexError, base64.binascii.Error):
                raise serializers.ValidationError("Invalid base64 image data.")

        return super().to_internal_value(data)
