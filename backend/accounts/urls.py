from django.urls import path

from .api.views import RegisterApiView, VerifyEmailApiView, ResendVerifyEmailViewApi

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name='register'),
    path('email-verify/', VerifyEmailApiView.as_view(), name='email-verify'),
    path('resend-link/', ResendVerifyEmailViewApi.as_view(), name='resend-link')
]
