from os import stat
from django.urls import reverse
from django.conf import settings
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site

import jwt
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.utils import Util
from .serializers import RegisterSerializer


class RegisterApiView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token

        current_sites = get_current_site(request)
        relative_link = reverse('email-verify')
        verify_email_url = 'http://'+current_sites.domain + \
            relative_link+"?token="+str(token)

        # to added email body from this view file, uncomment line below and comment the email_body line
        # calling loader function and context variables.
        # email_body = 'Hi '+user.email+' \nUse link below to verify your email \n'+verify_email_url

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

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmailApiView(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        print('token: ', token)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            print("\n payload: ", payload)
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
