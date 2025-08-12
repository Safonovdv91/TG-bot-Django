import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils import timezone

from g_cup_site.models import (
    AthleteModel,
    ChampionshipModel,
    CityModel,
    CountryModel,
    MotorcycleModel,
    StageModel,
    StageResultModel,
)
from g_cup_site.utils import APIGetter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Получение данных из Gymkhana-cup и их импорт в базу данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "--years",
            type=str,
            help='Разброс в годах - когда необходимо получить выборку данных(format: "start_year-end_year")',
        )
        parser.add_argument(
            "--type",
            type=str,
            default="gp",
            help="Тип чемпионата (gp, offline, online)",
        )

    def handle(self, *args, **options):
        api = APIGetter()
        logger.info("Начинаем получение данных...")
        years = options.get("years")
        logger.info("years = %s", years)
        champ_type = options.get("type")
        logger.info("champ_type = %s", champ_type)

        if years:
            from_year, to_year = map(int, years.split("-"))
        else:
            from_year = to_year = None

        self.stdout.write(self.style.SUCCESS("Starting data import..."))

        try:
            with transaction.atomic():
                self.import_championships(api, champ_type, from_year, to_year)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Data import championships completed successfully!"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {str(e)}"))
            raise

    def import_championships(self, api, champ_type, from_year, to_year):
        championships = api.get_data_championships(
            champ_type=champ_type, from_year=from_year, to_year=to_year
        )
        logger.info("Данные по чемпионатам получены.")

        for champ_data in championships:
            # Создаем или обновляем чемпионат
            champ, created = ChampionshipModel.objects.update_or_create(
                champ_id=champ_data["id"],
                defaults={
                    "title": champ_data["title"],
                    "year": champ_data["year"],
                    "description": champ_data.get("description", ""),
                    "champ_type": champ_type,
                },
            )
            if created:
                logger.info(f"Чемпионат: {champ.title}, создан: {created}")

            # Получаем полные данные по чемпионату
            full_data = api.get_data_championships_by_id(champ.champ_id, champ_type)

            if full_data:
                self.import_stages(api, champ, full_data.get("stages", []))

    def import_stages(self, api, championship, stages_data: list | None):
        logger.info(f"Начинаем импорт данных этапов... чампионат: {championship.title}")
        if not stages_data:
            return

        for stage_data in stages_data:
            logger.info(
                f"Импорт данных этапа: #{stage_data['id']} {stage_data['title']}"
            )
            stage, created = StageModel.objects.update_or_create(
                stage_id=stage_data["id"],
                championship=championship,
                defaults={
                    "status": stage_data["status"],
                    "title": stage_data["title"],
                    "stage_class": "A",
                    "track_url": stage_data.get("trackUrl"),
                    "date_start": self.parse_unix_time(stage_data.get("dateStart")),
                    "date_end": self.parse_unix_time(stage_data.get("dateEnd")),
                },
            )

            if created:
                logger.info(f"Этап: {stage.title}, Добавлен в базу данных:{created}")

            # Импортируем результаты ЭТАПА
            if created or stage.status in ("Предстоящий этап"):
                stage_results = api.data_stage(stage.stage_id, championship.champ_type)
                if stage_results:
                    self.import_results(stage, stage_results.get("results", []))

    def import_results(self, stage, results_data):
        if not results_data:
            logger.info("Данных по результатам этапа нет.")
            return
        logger.info("Данные по результатам этапа получены. Загружаем результаты этапа.")
        for result_data in results_data:
            country, _ = CountryModel.objects.get_or_create(
                title=result_data["userCountry"]
            )

            city, _ = CityModel.objects.get_or_create(
                title=result_data["userCity"], country=country
            )

            athlete, _ = AthleteModel.objects.get_or_create(
                id=result_data["userId"],
                defaults={
                    "first_name": result_data["userFirstName"],
                    "last_name": result_data["userLastName"],
                    "city": city,
                    "sportsman_class": result_data.get("athleteClass", "N"),
                    "img_url": result_data.get("imgUrl"),
                    "number": result_data.get("number"),
                },
            )

            motorcycle, _ = MotorcycleModel.objects.get_or_create(
                title=result_data["motorcycle"]
            )
            # Создаем результат этапа
            try:
                stage_result = StageResultModel.objects.update_or_create(
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
                logger.info(f"Результат {stage_result} добавлен в базу данных")

            except IntegrityError as e:
                logger.exception(
                    f"stage_result: {result_data} не добавлен в базу данных: {e}"
                )
                logger.exception(
                    "При добавлении данных возникло исключение с ошибкой уникальности."
                )
                return
            except Exception as e:
                logger.exception(
                    f"stage_result: {result_data} не добавлен в базу данных: {e}"
                )
                logger.exception("При добавлении данных возникло исключение.")

    @staticmethod
    def parse_unix_time(timestamp):
        if timestamp:
            naive_datetime = datetime.fromtimestamp(timestamp)
            return timezone.make_aware(naive_datetime)
        return None
