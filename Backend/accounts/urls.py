from django.urls import path

from .api.views import RegisterApiView

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name="register"),
]
