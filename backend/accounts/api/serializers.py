from django.contrib import auth
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

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


class ResetPasswordCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True
    )
    token = serializers.CharField(min_length=6, write_only=True)
    uidb64 = serializers.CharField(
        max_length=68,
        min_length=1,
        write_only=True
    )

    class Meta:
        fields = ['__all__']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            userId = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=userId)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(
                    'The password reset link is invalid',
                    401
                )

            user.set_password(password)
            user.save()

            return super().validate(attrs)
        except Exception:
            raise AuthenticationFailed(
                'The password reset link is invalid',
                401
            )
