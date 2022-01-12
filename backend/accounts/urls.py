from django.urls import path

from .api.views import RegisterApiView, VerifyEmailApiView, ResendVerifyEmailViewApi, LoginApiView

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name='register'),
    path('email-verify/', VerifyEmailApiView.as_view(), name='email-verify'),
    path('resend-link/', ResendVerifyEmailViewApi.as_view(), name='resend-link'),
    path('login/', LoginApiView.as_view(), name='login')
]
