import logging
import os
from abc import abstractmethod
from datetime import datetime
from enum import EnumType
from typing import Dict, List

import httpx
from django.contrib.auth import get_user_model
from django.utils import timezone
from dotenv import load_dotenv
from g_cup_site.models import (
    AthleteModel,
    BaseFigureModel,
    BaseFigureSportsmanResultModel,
    CityModel,
    CountryModel,
    MotorcycleModel,
    StageModel,
    StageResultModel,
)
from gymkhanagp.models import SportsmanClassModel, Subscription
from gymkhanagp.tasks import send_telegram_message_task
from users.utils import AdminNotifier, get_telegram_id

load_dotenv()
logger = logging.getLogger(__name__)
User = get_user_model()


class TypeChampionship(EnumType):
    GGP = "gp"
    BASE = "base"


class APIGetter:
    def __init__(self):
        self.url = os.environ.get("GYMKHANA_CUP_URL")
        self.api_key = os.environ.get("GYMKHANA_CUP_TOKEN")

    def _make_request(self, url_endpoint: str, params: dict) -> dict:
        """Запрос данных с уведомлением и логированием ошибок"""
        logger.info("Делаем запрос к /%s", url_endpoint)

        if self.url is None:
            logger.exception("Отсутствует адрес GYMKHANA_CUP_URL в os.environ")
            return {}

        url: str = self.url + url_endpoint
        full_params = {"signature": self.api_key, **params}
        try:
            response = httpx.get(url, params=full_params)
        except Exception as e:
            logger.exception("Ошибка при запросе к %s", url_endpoint, exc_info=e)
            return {}

        if response.status_code == 200:
            logger.info(
                "Server response [%s] %s", response.status_code, response.json()
            )
            return response.json()
        else:
            status_code = response.status_code
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text

            if 400 <= status_code <= 499:
                logger.error(
                    "Не удалось выполнить запрос, получена ошибка клиента[%s]:\n%s",
                    response.status_code,
                    error_body,
                )
                error_msg = f"При запросе на сервер получена ошибка клиентского запроса[{status_code}]\n[{error_body}]"
                AdminNotifier.notify_admin(message=error_msg)
            elif 500 <= status_code <= 599:
                logger.warning(
                    "Не удалось выполнить запрос, получена ошибка сервера[%s]:\n%s",
                    response.status_code,
                    error_body,
                )
            else:
                logger.error("Получен странный статус код %s", response.status_code)

            return {}

    def get_data_championships(
        self,
        champ_type: str,
        from_year: int | None = None,
        to_year: int | None = None,
    ):
        return self._make_request(
            "/championships/list",
            {
                "types": champ_type,
                "fromYear": from_year,
                "toYear": to_year,
            },
        )

    def get_data_championships_by_id(
        self, champ_id: int, champ_type: str = TypeChampionship.GGP
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

    def data_stage(self, stage_id: int, stage_type: str) -> {dict | None}:
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

    def get_figure_data(self, figure_id: int) -> dict | None:
        """Получает данные по фигуре"""
        url = f"{self.url}/figures/get"
        response = httpx.get(url, params={"signature": self.api_key, "id": figure_id})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {}

    def get_athlete_data(self, athlete_id: int) -> dict | None:
        """Получает данные по спортсмену"""
        url = f"{self.url}/users/get"
        response = httpx.get(url, params={"signature": self.api_key, "id": athlete_id})

        if response.status_code == 200:
            data = response.json()
            return data

        return {}


def get_subscribers_for_class(
    sport_class: str, competition_type: str = "gp"
) -> List[User]:
    """Получение подписчиков для указанного класса спортсменов."""
    subscriptions = Subscription.objects.filter(
        sportsman_class__name=sport_class,
        competition_type__name=competition_type,
    ).select_related("user_subscription__user", "sportsman_class", "competition_type")
    users_subscribed = [sub.user_subscription.user for sub in subscriptions]

    return users_subscribed


def notify_user_telegram_message(user: User, message: str) -> None:
    """Отправка уведомления в Telegram пользователю."""
    logger.info(f"Отправка уведомления в Telegram для пользователя {user.username}")
    telegram_id = get_telegram_id(user)
    if telegram_id and user.is_active:
        logger.info("Создаем задачу на отправку сообщения в Telegram")
        send_telegram_message_task.delay(telegram_id, message)
        logger.info(
            f"Уведомление отправлено в Telegram для пользователя {user.username}"
        )
        return

    logger.warning(f"Пользователь {user.username} не имеет Telegram ID или не активный")


class BaseHandler:
    """Базовый класс для обработчиков данных"""

    def __init__(self):
        self.api = APIGetter()
        self.changes = {
            "new_result": 0,
            "improved_result": 0,
            "no_change": 0,
        }
        self.entity = None
        self.entity_data = None
        self.COMPETITION_TYPE = None

    @abstractmethod
    def handle(self) -> None:
        pass

    def get_data(self) -> dict:
        return self.changes

    @staticmethod
    def parse_unix_time(timestamp: float) -> datetime | None:
        if timestamp:
            naive_datetime = datetime.fromtimestamp(timestamp)
            return timezone.make_aware(naive_datetime)
        return None

    @staticmethod
    def get_or_create_motorcycle(motorcycle_name: str) -> MotorcycleModel:
        motorcycle, _ = MotorcycleModel.objects.get_or_create(title=motorcycle_name)
        return motorcycle

    def get_or_create_athlete(self, athlete_data: Dict) -> AthleteModel:
        country, _ = CountryModel.objects.get_or_create(
            title=athlete_data["userCountry"]
        )
        city, _ = CityModel.objects.get_or_create(
            title=athlete_data["userCity"], country=country
        )
        athlete = AthleteModel.objects.filter(id=athlete_data.get("userId")).first()
        if not athlete:
            athlete_data = self.api.get_athlete_data(athlete_data.get("userId"))
            athlete = AthleteModel.objects.create(
                id=athlete_data.get("id"),
                first_name=athlete_data.get("firstName"),
                last_name=athlete_data.get("lastName"),
                city=city,
                sportsman_class=athlete_data.get("class", "N"),
            )
            return athlete

        return athlete

    def _send_class_notifications(
        self, sport_class: str, message: str, entity_title: str
    ) -> None:
        """Отправка уведомлений для класса спортсменов"""
        if not sport_class:
            raise ValueError("Класс спортсменов не указан")

        subscribers = get_subscribers_for_class(
            sport_class, competition_type=self.COMPETITION_TYPE
        )
        athlete_class = SportsmanClassModel.objects.get(
            name=sport_class,
        )

        for subscriber in subscribers:
            formatted_message = (
                f"{entity_title}\n\n"
                f"{athlete_class.subscribe_emoji} [{sport_class}] {message}\n"
            )
            notify_user_telegram_message(subscriber, formatted_message)

    def _handle_creation_notification(
        self, result_data: Dict, athlete: AthleteModel, entity_title: str
    ) -> None:
        """Обработка уведомления о новом результате"""
        entity_title = "🆕 " + entity_title
        if result_data.get("percent") == 100:
            entity_title += "\n\n ❗❗ Новый лидер этапа: ❗❗"
        message = (
            f"{athlete.full_name}\n"
            f"Время: {result_data['resultTime']} [{result_data['percent']}%]\n"
            f"Мотоцикл: {result_data.get('motorcycle', '---')}\n"
            f"Город: {result_data.get('userCity', '---')}\n"
            f"Видео: {result_data.get('video', '')}"
        )

        athlete_class = result_data.get("athleteClass")
        if not athlete_class:
            athlete_class = athlete.sportsman_class

        self._send_class_notifications(
            athlete_class,
            message,
            entity_title,
        )

    def _update_existing_result(
        self,
        existing_result: BaseFigureSportsmanResultModel | StageResultModel,
        result_data: Dict,
        new_time: int,
    ) -> None:
        """Обновление существующего результата"""
        old_time = existing_result.result_time
        time_diff = (existing_result.result_time_seconds - new_time) / 1000

        existing_result.result_time_seconds = new_time
        existing_result.result_time = result_data["resultTime"]
        existing_result.fine = result_data.get("fine", existing_result.fine)
        existing_result.video = result_data.get("video", existing_result.video)
        existing_result.save()

        self._handle_improvement_notification(
            result_data,
            existing_result.user,
            old_time,
            time_diff,
            self.entity.title,
        )
        self.changes["improved_result"] += 1

    def _handle_improvement_notification(
        self,
        result_data: Dict,
        athlete: AthleteModel,
        old_time: str,
        time_diff: float,
        entity_title: str,
    ) -> None:
        """Обработка уведомления об улучшении результата"""
        entity_title = "⬆️ " + entity_title
        if result_data.get("percent") == 100:
            entity_title += "\n\n ❗❗ Новый лидер этапа: ❗❗"
        message = (
            f"{athlete.full_name}\n"
            f"Старое время: {old_time}\n"
            f"Новое время: {result_data['resultTime']} [{result_data['percent']}%] "
            f"(⬆️{time_diff:.2f})\n"
            f"Мотоцикл: {result_data.get('motorcycle', '---')}\n"
            f"Город: {result_data.get('userCity', '---')}\n"
            f"Видео: {result_data.get('video', '')}"
        )

        athlete_class = result_data.get("athleteClass")
        if not athlete_class:
            athlete_class = athlete.sportsman_class

        self._send_class_notifications(athlete_class, message, entity_title)

    def _handle_no_change(self, athlete: AthleteModel) -> None:
        """Обработка отсутствия изменений"""
        self.changes["no_change"] += 1
        logger.info(f"Без изменений: {athlete.full_name} в этапе {self.entity.title}")


class StageGGPHandeler(BaseHandler):
    """Обработчик данных этапа ГПП"""

    def __init__(self, stage_id: int):
        super().__init__()
        self.COMPETITION_TYPE = "ggp"
        self.stage_id = stage_id

    def handle(self) -> None:
        try:
            self._import_single_stage()
            self._log_import_results()
        except Exception as e:
            logger.exception(f"Ошибка при импорте данных этапа: {e}")

    def _import_single_stage(self) -> None:
        """Импорт данных для одного этапа"""
        logger.info(f"Начинаем импорт этапа: {self.COMPETITION_TYPE}|{self.stage_id}")

        self.entity_data = self.api.data_stage(self.stage_id, "gp")
        if not self.entity_data:
            logger.warning(
                f"Нет данных для этапа: {self.COMPETITION_TYPE}|{self.stage_id}"
            )
            return

        self.entity, _ = StageModel.objects.get_or_create(
            stage_id=self.entity_data["id"]
        )
        self._process_results()

    def _process_results(self) -> None:
        """Обработка всех результатов этапа"""
        for result_data in self.entity_data.get("results", []):
            self._process_single_result(result_data)

    def _process_single_result(self, result_data: Dict) -> None:
        """Обработка одного результата"""
        new_time = result_data.get("resultTimeSeconds")
        if not new_time:
            logger.warning(f"Отсутствует время для результата: {result_data}")
            return

        athlete = self.get_or_create_athlete(result_data)
        existing_result = StageResultModel.objects.filter(
            stage=self.entity, user=athlete
        ).first()

        if not existing_result:
            self._create_new_result(result_data, athlete)
        elif new_time < existing_result.result_time_seconds:
            self._update_existing_result(existing_result, result_data, new_time)
        else:
            self._handle_no_change(athlete)

    def _create_new_result(self, result_data: Dict, athlete: AthleteModel) -> None:
        """Создание нового результата этапа"""
        motorcycle = self.get_or_create_motorcycle(result_data["motorcycle"])
        StageResultModel.objects.create(
            stage=self.entity,
            user=athlete,
            motorcycle=motorcycle,
            date=self.parse_unix_time(result_data["date"]),
            place=result_data.get("place", 0),
            fine=result_data.get("fine", 0),
            result_time_seconds=result_data["resultTimeSeconds"],
            result_time=result_data["resultTime"],
            video=result_data.get("video"),
        )
        self._handle_creation_notification(result_data, athlete, self.entity.title)
        self.changes["new_result"] += 1

    def _log_import_results(self) -> None:
        """Логирование результатов импорта"""
        logger.info(
            f"Импорт завершен. Новые: {self.changes['new_result']}, "
            f"Улучшенные: {self.changes['improved_result']}, "
            f"Без изменений: {self.changes['no_change']}"
        )


class BaseFigureHandler(BaseHandler):
    """Обработчик базовых фигур"""

    def __init__(self, figure_id: int):
        super().__init__()
        self.figure_id = figure_id
        self.figure = self._get_or_create_figure()
        self.COMPETITION_TYPE = "base"

    def handle(self) -> None:
        try:
            self._import_figure_results()
            self._log_import_results()
        except Exception as e:
            logger.exception(f"Ошибка при импорте данных фигуры: {e}")

    def _get_or_create_figure(self) -> BaseFigureModel:
        """Получение или создание базовой фигуры"""
        self.entity = BaseFigureModel.objects.filter(id=self.figure_id).first()
        if self.entity:
            return self.entity

        figure_data = self.api.get_figure_data(self.figure_id)
        if not figure_data:
            logger.error(f"Нет данных для фигуры ID {self.figure_id}")
            raise ValueError(f"Invalid figure ID: {self.figure_id}")

        return BaseFigureModel.objects.create(
            id=figure_data["id"],
            title=figure_data["title"],
            description=figure_data["description"],
            track=figure_data["track"],
            with_in_class=figure_data["withIncClass"],
        )

    def _import_figure_results(self) -> None:
        """Импорт результатов для фигуры"""
        logger.info(f"Начинаем импорт фигуры {self.figure.title}")
        figure_data = self.api.get_figure_data(self.figure.id)

        for result_data in figure_data.get("results", []):
            self._process_single_result(result_data)

    def _process_single_result(self, result_data: Dict) -> None:
        """Обработка одного результата фигуры"""
        best_result = result_data.get("best")
        if not best_result:
            return

        athlete = self._prepare_athlete_data(result_data)
        existing_result = BaseFigureSportsmanResultModel.objects.filter(
            base_figure=self.figure, user=athlete
        ).first()

        if not existing_result:
            self._create_new_figure_result(best_result, athlete)
        elif best_result.get("timeSeconds") < existing_result.result_time_seconds:
            self._update_existing_result(
                existing_result, result_data.get("best"), best_result.get("timeSeconds")
            )
        else:
            self._handle_no_change(athlete)

    def _prepare_athlete_data(self, result_data: Dict) -> AthleteModel:
        """Подготовка данных спортсмена"""

        athlete_data = {
            "userId": result_data["userId"],
            "userFirstName": result_data["userFirstName"],
            "userLastName": result_data["userLastName"],
            "userCity": result_data["userCity"],
            "userCountry": result_data["userCountry"],
        }
        return self.get_or_create_athlete(athlete_data)

    def _create_new_figure_result(
        self, result_data: Dict, athlete: AthleteModel
    ) -> None:
        """Создание нового результата для фигуры"""
        motorcycle = self.get_or_create_motorcycle(result_data["motorcycle"])
        BaseFigureSportsmanResultModel.objects.create(
            base_figure=self.figure,
            user=athlete,
            motorcycle=motorcycle,
            date=self.parse_unix_time(result_data.get("date")),
            fine=result_data.get("fine", 0),
            result_time_seconds=result_data["resultTimeSeconds"],
            result_time=result_data["resultTime"],
            video=result_data.get("video"),
        )
        self._handle_creation_notification(result_data, athlete, self.figure.title)
        self.changes["new_result"] += 1

    def _log_import_results(self) -> None:
        """Логирование результатов импорта"""
        logger.info(
            f"Импорт фигуры {self.figure.title} завершен. "
            f"Новые результаты: {self.changes['new_result']}"
        )
