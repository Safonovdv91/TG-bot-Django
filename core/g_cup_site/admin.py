from django.contrib import admin

from .models import *


@admin.register(ChampionshipModel)
class ChampionshipModelAdmin(admin.ModelAdmin):
    list_display = ("champ_id", "champ_type", "title", "year", "description")


@admin.register(StageModel)
class StageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "stage_id", "championship", "status", "title", "stage_class")


@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title")


@admin.register(AthleteModel)
class AthleteModelAdmin(admin.ModelAdmin):
    list_display = ("id", "sportsman_class", "number", "full_name", "city")


@admin.register(StageResultModel)
class StageResultModelAdmin(admin.ModelAdmin):
    list_display = (
        "stage",
        "user",
        "motorcycle",
        "date",
        "place",
        "fine",
        "result_time_seconds",
        "result_time",
        "video",
    )
