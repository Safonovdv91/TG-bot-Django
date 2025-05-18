import logging

from django.core.management.base import BaseCommand, CommandError

from g_cup_site.models import (
    StageModel,
    AthleteModel,
)
from g_cup_site.utils import BaseFigureHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Получение данных о проезде базовой фигуры."

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.changes = {
            "new_result": 0,
            "improved_result": 0,
            "no_change": 0,
        }
        self.verbose = False

    def _handle_no_change(self, athlete: AthleteModel, stage: StageModel) -> None:
        """Обработка случая без изменений."""
        self.changes["no_change"] += 1
        if self.verbose:
            log_message = (
                f"Без изменений: {athlete.first_name} {athlete.last_name} "
                f"в базовой фигуре {stage.title}"
            )
            logger.info(log_message)

    def add_arguments(self, parser):
        parser.add_argument(
            "--figure-id",
            type=int,
            help="ID базовой фигуры",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Подробный вывод информации",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        figure_id = options["figure_id"]
        if not figure_id:
            raise CommandError("--stage-id обязательный параметр")

        try:
            stage_results = BaseFigureHandler(figure_id)
            stage_results.handle()

        except Exception as e:
            logger.exception(f"Ошибка при импорте данных: {e}")
            raise CommandError(f"Ошибка при импорте данных: {e}")

        logger.info(f"Изменения в базе данных: {stage_results.changes}")
