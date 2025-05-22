import logging

from django.core.management.base import BaseCommand, CommandError

from g_cup_site.models import (
    StageModel,
    AthleteModel,
)
from g_cup_site.utils import APIGetter, StageGGPHandeler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Получение данных о странах и их импорт в базу данных одного этапа ГГП"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = APIGetter()
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
                f"в этапе {stage.title}"
            )
            logger.info(log_message)

    def add_arguments(self, parser):
        parser.add_argument(
            "--stage-id",
            type=int,
            help="ID этапа",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Подробный вывод информации",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        stage_id = options["stage_id"]
        if not stage_id:
            raise CommandError("--stage-id обязательный параметр")

        try:
            stage_results = StageGGPHandeler(stage_id)
            stage_results.handle()
            print(stage_results)

        except Exception as e:
            logger.exception(f"Ошибка при импорте данных: {e}")
            raise CommandError(f"Ошибка при импорте данных: {e}")

        logger.info(f"Изменения в базе данных: {stage_results.changes}")
