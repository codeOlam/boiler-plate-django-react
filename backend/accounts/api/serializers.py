from django.urls import reverse
from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError

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
        fields = ['email']

    def validate(self, attrs):
        try:
            email = attrs['data'].get('email', '')

            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)

                uidb64 = urlsafe_base64_encode(user.id)
                generate_token = PasswordResetTokenGenerator()
                token = generate_token.make_token(user)

                current_sites = get_current_site(
                    request=attrs['data'].get('request'))
                relative_link = reverse('email-verify')
                verify_email_url = 'http://'+current_sites.domain + \
                    relative_link+"?token="+str(token)
                email_body = 'Hi '+user.email + \
                    ' \nUse link below to verify your email \n'+verify_email_url

                email_data = {
                    'email_subject': 'Resent verification email',
                    'email_body': email_body,
                    'to_email': user.email,
                }

                Util.send_email(email_data)
            return attrs
        except:
            pass
        return super().validate(attrs)
