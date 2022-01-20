from django.contrib import auth


from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from accounts.utils import Util
from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    # You can add custom validation method below
    # To validate your fields
    # e.g
    # def validate(self, attrs):
    #     email = attrs.get('email', '')
    #     return attrs

    def create(self, validate_data):
        return User.objects.create_user(**validate_data)


class ResendActivationEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed(
                'Login failed. Please enter valid credentials.'
            )

        return {
            'email': user.email,
        }


class PasswordRestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email']
