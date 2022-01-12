from django.urls import path

from .api.views import RegisterApiView, VerifyEmailApiView

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name="register"),
    path('email-verify/', VerifyEmailApiView.as_view(), name="email-verify"),
]
