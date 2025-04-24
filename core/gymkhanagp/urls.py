from django.urls import path
from . import views

app_name = "gymkhanagp"
urlpatterns = [
    path("", views.index, name="index"),
]
