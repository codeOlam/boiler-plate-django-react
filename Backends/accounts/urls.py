from django.urls import path

from accounts.api.registration import RegisterApi

urlpatterns = [
    path('register/', RegisterApi.as_view(), name="register"),
]
