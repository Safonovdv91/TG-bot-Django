from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "user",
        "created_at",
        "updated_at",
        "source",
        "report_type",
        "resolved",
    )
    list_display_links = ("user",)
    ordering = ("report_type", "-created_at")
    list_filter = ("resolved", "report_type")

    list_per_page = 30
