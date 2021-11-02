from rest_framework import serializers

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email", " ")
        password = attrs.get("password", "")

        if not email:
            raise serializers.ValidationError("Email Required!")

        if not password:
            raise serializers.ValidationError("Password Required!")

        return super().validate(attrs)

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)
