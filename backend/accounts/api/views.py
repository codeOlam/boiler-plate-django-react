from os import stat
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
from .serializers import RegisterSerializer, ResendActivationEmailSerializer, EmailVerificationSerializer


class RegisterApiView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user)
        print('\ntoken: ', token)

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

        return Response(
            {'Message': 'Verification email has been sent to your email'},
            status=status.HTTP_201_CREATED
        )


class ResendVerifyEmailViewApi(generics.GenericAPIView):
    serializer_class = ResendActivationEmailSerializer

    def post(self, request):
        user_data = request.data
        user_email = user_data['email']

        try:
            user = User.objects.get(email=user_email)

            if user.user.is_verified:
                return Response({'Message': 'This user is already verified'})

            token = RefreshToken.for_user(user).access_token
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

            return Response(
                {'Message': 'Verification email has been resent to your email'},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {'error': 'This user does not exist.'},
                status=status.HTTP_404_NOT_FOUND
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

            return Response({'email': 'Email successfully activate'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Link is expired!'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.DecodeError:
            return Response({'error': 'Invalid Activation Link!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
