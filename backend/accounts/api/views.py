from django.urls import reverse
from django.conf import settings
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site

import jwt
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User
from accounts.utils import Util
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    EmailVerificationSerializer,
    ResendActivationEmailSerializer
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
        verify_email_url = 'http://'+current_sites.domain + \
            relative_link+"?token="+str(token)

        context = {
            'user': user,
            'site_name': current_sites.name,
            'verify_email_url': verify_email_url
        }
        email_body = loader.render_to_string(
            'registration/verify-email.html',
            context
        )

        email_data = {
            'email_subject': 'Please Verify your email',
            'email_body': email_body,
            'to_email': user.email,
        }

        Util.send_email(email_data)

        response_payload = {
            'serializer_payload': serializer_payload,
            'Status': {
                'message': 'Verification email has been sent to your email',
                'code': f"{status.HTTP_201_CREATED} CREATED"
            },
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
                    'code': f"{status.status.HTTP_200_OK} OK"
                },
            }
            return Response(response_payload, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            expired_response_payload = {
                'status': {
                    'failed': 'Activation Link is expired!',
                    'code': f"{status.HTTP_401_UNAUTHORIZED} UNAUTHORIZED"
                },
            }
            return Response(expired_response_payload, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.DecodeError:
            decodeError_response_payload = {
                'status': {
                    'error': 'Invalid Activation Link!',
                    'code': f"{status.HTTP_406_NOT_ACCEPTABLE} NOT_ACCEPTABLE"
                },
            }
            return Response(decodeError_response_payload, status=status.HTTP_406_NOT_ACCEPTABLE)


class ResendVerifyEmailViewApi(generics.GenericAPIView):
    serializer_class = ResendActivationEmailSerializer

    def post(self, request):
        user_data = request.data
        user_email = user_data['email']

        try:
            user = User.objects.get(email=user_email)

            if user.user.is_verified:
                return Response({'Message': 'This user is already verified'})

            # This is used becacuse it is long lived compaired to access token
            token = RefreshToken.for_user(user)

            current_sites = get_current_site(request)
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

            response_payload = {
                'status': {
                    'message': 'Verification email has been resent to your email',
                    'code': f"{status.HTTP_201_CREATED} CREATED"
                },
            }
            return Response(response_payload, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            doesNotExist_response_payload = {
                'status': {
                    'error': 'This user does not exist.',
                    'code': f"{status.HTTP_404_NOT_FOUND} NOT_FOUND"
                },
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
            'token': tokens
        }

        return Response(response_payload, status=status.HTTP_200_OK)
