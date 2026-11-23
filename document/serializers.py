from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from .models import Document


class PDFUploadSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])]
    )


class DocumentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    file_url = serializers.FileField(source="file", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "user_id",
            "name",
            "file_url",
            "uploaded_at",
        ]


class DocumentSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, allow_blank=False)
    top_k = serializers.IntegerField(default=3, min_value=1, max_value=20)
    file_id = serializers.IntegerField(required=False, allow_null=True)
