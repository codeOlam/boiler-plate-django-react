from os import name
from django.urls import path

from .api.views import (
    RegisterApiView,
    VerifyEmailApiView,
    ResendVerifyEmailApiView,
    LoginApiView,
    PasswordResetApiView,
    PasswordTokenVerifyApiView,
)

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name='register'),
    path('email-verify/', VerifyEmailApiView.as_view(), name='email-verify'),
    path('resend-link/', ResendVerifyEmailApiView.as_view(), name='resend-link'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('password-reset/', PasswordResetApiView.as_view(), name='password-reset'),
    path('password-token-verify/<uidb64>/token/',
         PasswordTokenVerifyApiView.as_view(), name='password-token-verify'),
]
