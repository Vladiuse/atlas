from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'form_checker'

urlpatterns = [
    path('', views.index, name="index"),
]