import logging
from typing import Dict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from g_cup_site.models import (
    StageModel,
    CountryModel,
    CityModel,
    AthleteModel,
    MotorcycleModel,
    StageResultModel,
)
from g_cup_site.utils import APIGetter, TypeChampionship

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

    @staticmethod
    def get_or_create_motorcycle(motorcycle_name: str) -> MotorcycleModel:
        """Получение или создание мотоцикла."""
        motorcycle, _ = MotorcycleModel.objects.get_or_create(title=motorcycle_name)
        return motorcycle

    @staticmethod
    def get_or_create_athlete(athlete_data):
        country, _ = CountryModel.objects.get_or_create(
            title=athlete_data["userCountry"]
        )
        city, _ = CityModel.objects.get_or_create(
            title=athlete_data["userCity"], country=country
        )
        athlete, _ = AthleteModel.objects.get_or_create(
            id=athlete_data["userId"],
            defaults={
                "first_name": athlete_data["userFirstName"],
                "last_name": athlete_data["userLastName"],
                "city": city,
                "sportsman_class": athlete_data.get("athleteClass", "N"),
            },
        )
        return athlete

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
            "--championship-type",
            type=str,
            default="gp",
            help="Тип чемпионата (gp, offline, online)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Подробный вывод информации",
        )

    def handle(self, *args, **options):
        self.verbose = options["verbose"]
        stage_id = options["stage_id"]
        championship_type = options["championship_type"]

        if not stage_id:
            raise CommandError("--stage-id обязательный параметр")
        try:
            self.import_single_stage(stage_id, championship_type)
        except Exception as e:
            logger.exception(f"Ошибка при импорте данных: {e}")
            raise CommandError(f"Ошибка при импорте данных: {e}")

    def import_single_stage(self, stage_id: int, championship_type: str) -> None:
        """Импорт данных для одного этапа."""

        logger.info(f"Начинаем импорт данных о этапе: {championship_type}| {stage_id}")
        stage_data = self.api.data_stage(stage_id, stage_type=TypeChampionship.GP)
        if not stage_data:
            logger.warning(f"Нет данных для этапа: {championship_type}|{stage_id}")
            return

        logger.debug(f"Данные этапа: {stage_data}")
        self.import_results(stage_data)

    def import_results(self, stage_data: Dict) -> None:
        """Импорт результатов этапа."""

        logger.info("Импорт результатов этапа...")
        with transaction.atomic():
            stage, _ = StageModel.objects.get_or_create(stage_id=stage_data["id"])
            # todo если создан новый этап, то создаем новую запись в базе данных
            for result_data in stage_data.get("results", []):
                self.process_single_result(stage, result_data)

        logger.info(
            f"Импорт завершен. Новые: {self.changes['new_result']}, "
            f"Улучшенные: {self.changes['improved_result']}, "
            f"Без изменений: {self.changes['no_change']}"
        )

    def process_single_result(self, stage: StageModel, result_data: Dict) -> None:
        """Обработка одного результата этапа."""

        new_time = result_data.get("resultTimeSeconds")
        if not new_time:
            logger.warning(f"Отсутствует время для результата: {result_data}")
            return

        athlete = self.get_or_create_athlete(result_data)
        existing_result = StageResultModel.objects.filter(
            stage=stage, user=athlete
        ).first()
        if not existing_result:
            self.create_new_result(stage, athlete, result_data)

        elif new_time < existing_result.result_time_seconds:
            self.update_improved_result(existing_result, result_data, new_time)

        else:
            self._handle_no_change(athlete, stage)

    def create_new_result(
        self,
        stage: StageModel,
        athlete: AthleteModel,
        result_data: Dict,
    ) -> None:
        """Создание нового результата."""

        motorcycle = self.get_or_create_motorcycle(result_data["motorcycle"])
        stage_result = StageResultModel.objects.create(
            stage=stage,
            user=athlete,
            motorcycle=motorcycle,
            defaults={
                "date": self.parse_unix_time(result_data["date"]),
                "place": result_data.get("place", 0),
                "fine": result_data.get("fine", 0),
                "result_time_seconds": result_data["resultTimeSeconds"],
                "result_time": result_data["resultTime"],
                "video": result_data.get("video"),
            },
        )
        # todo ВЫсылаем сообщение для подписчиков(добавляем в очередь рассылок)
        self.changes["new_results"] += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"NEW RESULT: {athlete.first_name} {athlete.last_name} "
                f"added to stage {stage.title} with time {result_data['resultTime']}"
            )
        )
        logger.info(f"Результат {stage_result} добавлен в базу данных")

    def update_improved_result(
        self,
        existing_result: StageResultModel,
        result_data: Dict,
        new_time: float,
    ) -> None:
        """Обновление существующего результата."""
        old_time = existing_result.result_time_seconds
        time_diff = old_time - new_time

        existing_result.result_time_seconds = new_time
        existing_result.result_time = result_data["resultTime"]
        existing_result.place = result_data.get("place", existing_result.place)
        existing_result.fine = result_data.get("fine", existing_result.fine)
        existing_result.video = result_data.get("video", existing_result.video)
        existing_result.save()

        # todo Высылаем сообщение для подписчиков о улучшении результата(добавляем в очередь рассылок)
        self.changes["improved_result"] += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"IMPROVEMENT: {existing_result.user.first_name} "
                f"{existing_result.user.last_name} improved time in "
                f"stage {existing_result.stage.title} by "
                f"{time_diff / 1000:.3f} seconds "
                f"(new time: {result_data['resultTime']})"
            )
        )

    @staticmethod
    def parse_unix_time(timestamp):
        if timestamp:
            naive_datetime = datetime.fromtimestamp(timestamp)
            return timezone.make_aware(naive_datetime)
        return None
