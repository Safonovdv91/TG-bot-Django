from django.contrib import admin

from .models import (
    ChampionshipModel,
    StageModel,
    MotorcycleModel,
    AthleteModel,
    StageResultModel,
    BaseFigureModel,
    BaseFigureSportsmanResultModel,
)


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


@admin.register(BaseFigureModel)
class BaseFigureModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "track", "with_in_class")


@admin.register(BaseFigureSportsmanResultModel)
class BaseFigureSportsmanResultModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "base_figure",
        "user",
        "motorcycle",
        "date",
        "fine",
        "result_time_seconds",
        "result_time",
        "video",
    )
