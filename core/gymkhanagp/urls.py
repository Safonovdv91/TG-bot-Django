from django.urls import path
from . import views

app_name = "gymkhanagp"
urlpatterns = [
    path("", views.subscriptions_view, name="index"),
    path("subscribe/", views.subscribe_class, name="subscribe_class"),
    path("unsubscribe/", views.unsubscribe_class, name="unsubscribe_class"),
]
