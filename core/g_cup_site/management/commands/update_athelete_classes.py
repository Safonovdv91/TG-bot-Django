import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from g_cup_site.utils import APIGetter
from g_cup_site.models import (
    AthleteModel,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Обновление данных о спортсменах в базе данных"

    def handle(self, *args, **options):
        api = APIGetter()
        logger.info("Начинаем получение данных...")
        try:
            with transaction.atomic():
                athletes: list[AthleteModel] = AthleteModel.objects.all()
                print(f"Всего спортсменов: {len(athletes)}")
                for athlete in athletes:
                    print(f"Обновляем спортсмена: {athlete}")
                    fresh_athlete_data = api.get_athlete_data(athlete.id)
                    athlete.first_name = fresh_athlete_data.get("firstName")
                    athlete.last_name = fresh_athlete_data.get("lastName")
                    athlete.sportsman_class = fresh_athlete_data.get("class")
                    athlete.img_url = fresh_athlete_data.get("imgUrl")
                    athlete.number = fresh_athlete_data.get("number")

                    athlete.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        "Data import championships completed successfully!"
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {str(e)}"))
            raise
