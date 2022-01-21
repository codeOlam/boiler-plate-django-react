from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .api.views import (
    RegisterApiView,
    VerifyEmailApiView,
    ResendVerifyEmailApiView,
    LoginApiView,
    PasswordResetApiView,
    PasswordTokenVerifyApiView,
    ResetPasswordCompleteApiView,
)


urlpatterns = [
    path('register/', RegisterApiView.as_view(), name='register'),
    path('email-verify/', VerifyEmailApiView.as_view(), name='email-verify'),
    path('resend-link/', ResendVerifyEmailApiView.as_view(), name='resend-link'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetApiView.as_view(), name='password-reset'),
    path(
        'password-token-verify/<uidb64>/<token>/',
        PasswordTokenVerifyApiView.as_view(),
        name='password-token-verify'
    ),
    path(
        'reset-password-complete/',
        ResetPasswordCompleteApiView.as_view(),
        name='reset-password-complete'
    ),
]
