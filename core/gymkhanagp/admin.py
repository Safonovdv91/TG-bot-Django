from django.contrib import admin
from .models import (
    CompetitionTypeModel,
    SportsmanClassModel,
    Subscription,
    UserSubscription,
)


@admin.register(CompetitionTypeModel)
class CompetitionTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(SportsmanClassModel)
class SportsmanClassAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user_subscription", "competition_type", "sportsman_class")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "is_active")
