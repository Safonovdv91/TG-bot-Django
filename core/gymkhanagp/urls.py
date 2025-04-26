from django.urls import path
from . import views

app_name = "gymkhanagp"
urlpatterns = [
    path("", views.subscriptions_view, name="index"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("toggle_subscription/", views.toggle_subscription, name="toggle_subscription"),
]
