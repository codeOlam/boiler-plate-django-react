from django.core.validators import validate_email

from rest_framework import serializers

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')

        try:
            validate_email(email)
        except validate_email.ValidationError:
            raise serializers.ValidationError('This email is not valid')

        return attrs

    def creat(self, validate_data):
        return User.objects.create_user(**validate_data)
