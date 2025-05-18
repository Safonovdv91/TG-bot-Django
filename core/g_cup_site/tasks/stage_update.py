import logging

from django.db import transaction

from core import celery_app
from g_cup_site.models import AthleteModel
from g_cup_site.utils import StageGGPHandeler, BaseFigureHandler, APIGetter

logger = logging.getLogger(__name__)


@celery_app.task
def stage_update(stage_id: int):
    """Периодическое обновление этапа c переданным id."""
    stage_results = StageGGPHandeler(stage_id)
    stage_results.handle()


@celery_app.task
def base_figure_update(figure_id: int):
    """Получение результатов для базовой фигуры."""
    stage_results = BaseFigureHandler(figure_id)
    stage_results.handle()


def update_all_athletes_info():
    api = APIGetter()
    count = 0
    with transaction.atomic():
        athletes: list[AthleteModel] = AthleteModel.objects.all()
        for athlete in athletes:
            fresh_athlete_data = api.get_athlete_data(athlete.id)

            if athlete.sportsman_class != fresh_athlete_data.get("class"):
                count += 1

            athlete.first_name = fresh_athlete_data.get("firstName")
            athlete.last_name = fresh_athlete_data.get("lastName")
            athlete.sportsman_class = fresh_athlete_data.get("class")
            athlete.img_url = fresh_athlete_data.get("imgUrl")
            athlete.number = fresh_athlete_data.get("number")

            athlete.save()
    return f"Обновили класс {count} спортсменов из {len(athletes)}."
