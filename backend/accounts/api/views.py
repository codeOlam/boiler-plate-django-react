from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError

import jwt
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User
from accounts.utils import compose_email
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    EmailVerificationSerializer,
    ResendActivationEmailSerializer,
    PasswordRestSerializer,
    ResetPasswordCompleteSerializer,
)


class RegisterApiView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer_payload = serializer.data
        user = User.objects.get(email=serializer_payload['email'])

        # This is used becacuse it is long lived compaired to access token
        token = RefreshToken.for_user(user)

        current_sites = get_current_site(request)
        relative_link = reverse('email-verify')
        composed_url = 'http://'+current_sites.domain + \
            relative_link+"?token="+str(token)
        email_subject = 'Email Verification'

        compose_email(
            user,
            current_sites,
            composed_url,
            email_subject,
            'registration/verify-email.html',
        )

        response_payload = {
            'serializer_payload': serializer_payload,
            'Status': {
                'message': 'Verification email has been sent to your email',
                'code': f"{status.HTTP_201_CREATED} CREATED"
            },
            'response_code': status.HTTP_201_CREATED,
        }

        return Response(
            response_payload,
            status=status.HTTP_201_CREATED
        )


class VerifyEmailApiView(views.APIView):
    serializer_class = EmailVerificationSerializer

    # This is specific for swagger doc, to help you test verification tokens
    # manually.
    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY,
        description='Allow for manual input of verification token during test',
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            user = User.objects.get(id=payload['user_id'])

            # update user verification status
            if not user.is_verified:
                user.is_verified = True
                user.save()

            response_payload = {
                'status': {
                    'success': 'Email successfully activate',
                    'code': f"{status.HTTP_200_OK} OK"
                },
                'response_code': status.HTTP_200_OK,
            }
            return Response(response_payload, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            expired_response_payload = {
                'status': {
                    'failed': 'Activation Link is expired!',
                    'code': f"{status.HTTP_401_UNAUTHORIZED} UNAUTHORIZED"
                },
                'response_code': status.HTTP_401_UNAUTHORIZED,
            }
            return Response(expired_response_payload, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.DecodeError:
            decodeError_response_payload = {
                'status': {
                    'error': 'Invalid Activation Link!',
                    'code': f"{status.HTTP_406_NOT_ACCEPTABLE} NOT_ACCEPTABLE"
                },
                'response_code': status.HTTP_406_NOT_ACCEPTABLE,
            }
            return Response(decodeError_response_payload, status=status.HTTP_406_NOT_ACCEPTABLE)


class ResendVerifyEmailApiView(generics.GenericAPIView):
    serializer_class = ResendActivationEmailSerializer

    def post(self, request):
        user_data = request.data
        user_email = user_data['email']

        try:
            user = User.objects.get(email=user_email)

            if user.is_verified:
                return Response({'Message': 'This user is already verified'})

            # This is used becacuse it is long lived compaired to access token
            token = RefreshToken.for_user(user)

            current_sites = get_current_site(request)
            relative_link = reverse('email-verify')
            composed_url = 'http://'+current_sites.domain + \
                relative_link+"?token="+str(token)

            email_body = 'Hi '+user.email + \
                ' \nUse link below to verify your email \n'+composed_url

            email_subject = 'Resent Email Verification'

            compose_email(
                user,
                current_sites,
                composed_url,
                email_subject,
                in_line_content=email_body,
            )

            response_payload = {
                'status': {
                    'message': 'Verification link has been resent to your email',
                    'code': f"{status.HTTP_201_CREATED} CREATED"
                },
                'response_code': status.HTTP_201_CREATED,
            }
            return Response(response_payload, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            doesNotExist_response_payload = {
                'status': {
                    'error': 'This user does not exist.',
                    'code': f"{status.HTTP_404_NOT_FOUND} NOT_FOUND"
                },
                'response_code': status.HTTP_404_NOT_FOUND,
            }
            return Response(doesNotExist_response_payload, status=status.HTTP_404_NOT_FOUND)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=payload['email'])
        if user:
            tokens = user.tokens()

        serializer_payload = serializer.data

        response_payload = {
            'user_data': serializer_payload,
            'status': {
                'success': 'Login Successful',
                'code': f"{status.HTTP_200_OK} OK"
            },
            'token': tokens,
            'response_code': status.HTTP_200_OK,
        }

        return Response(response_payload, status=status.HTTP_200_OK)


class PasswordResetApiView(generics.GenericAPIView):
    serializer_class = PasswordRestSerializer

    def post(self, request):
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid()
        email = payload['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            generate_token = PasswordResetTokenGenerator()
            token = generate_token.make_token(user)

            current_sites = get_current_site(request)
            relative_link = reverse(
                'password-token-verify',
                kwargs={'uidb64': uidb64, 'token': token}
            )
            composed_url = 'http://'+current_sites.domain+relative_link
            email_subject = 'Reset Passowrd Link'

            compose_email(
                user,
                current_sites,
                composed_url,
                email_subject,
                'registration/reset-password.html',
            )

        serializer_payload = serializer.data

        response_payload = {
            'user_data': serializer_payload,
            'status': {
                'message': 'Password reset email has been sent',
                'code': f"{status.HTTP_201_CREATED} CREATED"
            },
            'response_code': status.HTTP_201_CREATED,
        }

        return Response(response_payload, status=status.HTTP_201_CREATED)


class PasswordTokenVerifyApiView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:

            userId = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=userId)

            if not PasswordResetTokenGenerator().check_token(user, token):
                response_payload = {
                    'status': {
                        'error': 'Token not valid, request a new token',
                        'code': f"{status.HTTP_401_UNAUTHORIZED} UNAUTHORIZED"
                    },
                    'response_code': status.HTTP_401_UNAUTHORIZED
                }

                return Response(response_payload, status=status.HTTP_401_UNAUTHORIZED)

            response_payload = {
                'status': {
                    'success': 'Token is valid',
                    'code': f"{status.HTTP_200_OK} OK"
                },
                'uidb64': uidb64,
                'token': token,
                'response_code': status.HTTP_200_OK,
            },

            return Response(response_payload, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            response_payload = {
                'status': {
                    'error': 'Token not valid, request a new token',
                    'code': f"{status.HTTP_401_UNAUTHORIZED} UNAUTHORIZED"
                },
                'response_code': status.HTTP_401_UNAUTHORIZED,
            }

            return Response(response_payload, status=status.HTTP_401_UNAUTHORIZED)


class ResetPasswordCompleteApiView(generics.GenericAPIView):
    serializer_class = ResetPasswordCompleteSerializer

    def patch(self, request):
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)

        response_payload = {
            'status': {
                'success': 'Password reset successful',
                'code': f"{status.HTTP_200_OK} OK"
            },
            'response_code': status.HTTP_200_OK,
        }

        return Response(response_payload, status=status.HTTP_200_OK)
