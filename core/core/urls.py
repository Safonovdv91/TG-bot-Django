from django.contrib import admin
from django.urls import path, include

from core.settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("ggp/", include("gymkhanagp.urls", namespace="gymkhanagp")),
    path("", include("index.urls", namespace="index")),
]
if DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

