import logging
import os
from datetime import datetime
from enum import EnumType
from typing import Dict

import httpx
from django.db import transaction
from django.utils import timezone
from dotenv import load_dotenv

from g_cup_site.models import (
    StageModel,
    MotorcycleModel,
    CountryModel,
    CityModel,
    AthleteModel,
    StageResultModel,
)

load_dotenv()
logger = logging.getLogger(__name__)


class TypeChampionship(EnumType):
    GP = "gp"
    CUP = "cup"


class APIGetter:
    def __init__(self):
        self.url = os.environ.get("G_CUP_URL")
        self.api_key = os.environ.get("G_CUP_API_KEY")

    def get_data_championships(
        self,
        champ_type: TypeChampionship = "gp",
        from_year: int | None = None,
        to_year: int | None = None,
    ):
        url = f"{self.url}/championships/list"
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "types": champ_type,
                "fromYear": from_year,
                "toYear": to_year,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def get_data_championships_by_id(
        self, champ_id: int, champ_type: TypeChampionship = "gp"
    ):
        url = f"{self.url}/championships/get"
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "id": champ_id,
                "type": champ_type,
            },
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def data_stage(
        self, stage_id: int, stage_type: TypeChampionship = "gp"
    ) -> {dict | None}:
        """Получает данные по этапам чемпионата"""
        url = f"{self.url}/stages/get?id=&type="
        response = httpx.get(
            url,
            params={
                "signature": self.api_key,
                "id": stage_id,
                "type": stage_type,
            },
        )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {}


class StageGGPHandeler:
    """Класс обработки данных одного этапа ГГП"""

    def __init__(self, stage_id: int, championship_type: str = "ggp") -> None:
        self.api = APIGetter()
        self.changes = {
            "new_result": 0,
            "improved_result": 0,
            "no_change": 0,
        }
        self.stage_id = stage_id
        self.championship_type = championship_type

    def handle(self) -> None:
        try:
            self._import_single_stage(self.stage_id, self.championship_type)
        except Exception as e:
            logger.exception(f"Ошибка при импорте данных: {e}")

    def _import_single_stage(self, stage_id: int, championship_type: str) -> None:
        """Импорт данных для одного этапа."""

        logger.info(f"Начинаем импорт данных о этапе: {championship_type}| {stage_id}")

        stage_data_from_api = self.api.data_stage(stage_id)
        if not stage_data_from_api:
            logger.warning(f"Нет данных для этапа: {championship_type}|{stage_id}")
            return

        logger.debug(f"Данные этапа: {stage_data_from_api}")
        self._import_results(stage_data_from_api)

    def _import_results(self, stage_data_from_api: Dict) -> None:
        """Импорт результатов этапа."""

        logger.info("Импорт результатов этапа...")
        with transaction.atomic():
            self.stage, created = StageModel.objects.get_or_create(
                stage_id=stage_data_from_api["id"]
            )

            if created:
                pass
                # todo если создан новый этап, то создаем новую запись в базе данных

            for result_data in stage_data_from_api.get("results", []):
                self._process_single_result(self.stage, result_data)

        logger.info(
            f"Импорт завершен. Новые: {self.changes['new_result']}, "
            f"Улучшенные: {self.changes['improved_result']}, "
            f"Без изменений: {self.changes['no_change']}"
        )

    def _process_single_result(self, stage: StageModel, result_data: Dict) -> None:
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
        StageResultModel.objects.create(
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
        logger.info(
            f"NEW RESULT: {athlete.first_name} {athlete.last_name} "
            f"added to stage {self.stage.title} with time {result_data['resultTime']}"
        )

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
        logger.info(
            f"IMPROVEMENT: {existing_result.user.first_name} "
            f"{existing_result.user.last_name} improved time in "
            f"stage {existing_result.stage.title} by "
            f"{time_diff / 1000:.3f} seconds "
            f"(new time: {result_data['resultTime']})"
        )

    @staticmethod
    def parse_unix_time(timestamp):
        if timestamp:
            naive_datetime = datetime.fromtimestamp(timestamp)
            return timezone.make_aware(naive_datetime)
        return None

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
        logger.info(
            f"Без изменений: {athlete.first_name} {athlete.last_name} "
            f"в этапе {stage.title}"
        )
