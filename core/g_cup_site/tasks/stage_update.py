import logging

from core import celery_app
from g_cup_site.utils import StageGGPHandeler, BaseFigureHandler

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
