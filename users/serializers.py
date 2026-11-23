# users/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "password"]

    def create(self, validated_data):
        # Calls UserManager.create_user(), which hashes the password automatically
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
