from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include("form_checker.urls")),
    path("landing_preview/", include("landing_preview.urls")),
]
