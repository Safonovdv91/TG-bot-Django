from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("ggp/", include("gymkhanagp.urls", namespace="gymkhanagp")),
    path("", include("index.urls", namespace="index")),
] + debug_toolbar_urls()
