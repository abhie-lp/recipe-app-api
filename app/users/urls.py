from . import views
from django.urls import path

app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserAPIView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
]
