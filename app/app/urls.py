from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/user/", include("users.urls", namespace="user")),
    path('admin/', admin.site.urls),
]
