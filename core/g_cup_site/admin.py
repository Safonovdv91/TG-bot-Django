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
    list_display = ("title", "champ_type", "year", "description")


@admin.register(StageModel)
class StageModelAdmin(admin.ModelAdmin):
    list_display = ("title", "stage_id", "championship", "results_count", "status")
    list_filter = ("status", "championship")
    ordering = ("championship", "-stage_id")
    list_per_page = 30

    def results_count(self, obj):
        return obj.results.count()

    results_count.short_description = "Количество результатов"


@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(admin.ModelAdmin):
    list_display = ("title", "results_count", "results_count_ggp", "results_count_base")
    ordering = ("results_base_figure", "results_base_figure", "results")
    list_per_page = 50

    def results_count_base(self, obj):
        return obj.results_base_figure.count()

    def results_count_ggp(self, obj):
        return obj.results.count()

    def results_count(self, obj):
        ggp = self.results_count_base(obj)
        base = self.results_count_ggp(obj)
        return ggp + base

    results_count_base.short_description = "Количество результатов на Base"
    results_count_ggp.short_description = "Количество результатов в GGP"
    results_count.short_description = "Количество результатов"


@admin.register(AthleteModel)
class AthleteModelAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "sportsman_class",
        "number",
        "city",
        "results_count_ggp",
        "results_count_base",
    )
    search_fields = ("city__title", "first_name", "last_name")
    list_select_related = ("city",)

    list_per_page = 50

    def results_count_ggp(self, obj):
        return obj.results.count()

    def results_count_base(self, obj):
        return obj.results_base_figure.count()

    results_count_ggp.short_description = "Количество результатов GGP"
    results_count_base.short_description = "Количество результатов базы"


@admin.register(StageResultModel)
class StageResultModelAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "motorcycle",
        "stage",
        "date",
        "place",
        "fine",
        "result_time_seconds",
        "result_time",
        "video",
    )
    list_filter = ("stage", "date", "motorcycle")
    ordering = ("-date", "result_time_seconds")

    select_related = ("motorcycle",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("motorcycle")


@admin.register(BaseFigureModel)
class BaseFigureModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "id",
        "description",
        "track",
        "results_count",
        "with_in_class",
    )

    def results_count(self, obj):
        return obj.results_base_figure.count()

    results_count.short_description = "Количество результатов"


@admin.register(BaseFigureSportsmanResultModel)
class BaseFigureSportsmanResultModelAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "base_figure",
        "motorcycle",
        "date",
        "fine",
        "result_time_seconds",
        "result_time",
        "video",
    )
