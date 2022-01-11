from django.urls import reverse
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site

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

        current_sites = get_current_site(request).domain
        relative_link = reverse('email-verify')
        site_url = 'http://'+current_sites+relative_link+"?token="+str(token)
        email_body = 'Hi '+user.email+' \nUse link below to verify your email \n'+site_url
        email_data = {
            'email_subject': 'Please Verify your email',
            'email_body': email_body}

        Util.send_email(email_data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmailApiView(generics.GenericAPIView):
    def get(self):
        pass
