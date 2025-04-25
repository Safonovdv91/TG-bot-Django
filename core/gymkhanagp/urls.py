from django.urls import path
from . import views

app_name = "gymkhanagp"
urlpatterns = [
    path("", views.index, name="index"),
    path("delete/<int:pk>/", views.delete_subscription, name="delete_subscription"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("toggle_subscription/", views.toggle_subscription, name="toggle_subscription"),
]
