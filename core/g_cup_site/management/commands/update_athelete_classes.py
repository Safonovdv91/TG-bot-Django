import logging

from django.core.management.base import BaseCommand

from g_cup_site.tasks import update_all_athletes_info

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Обновление данных о спортсменах в базе данных"

    def handle(self, *args, **options):
        update_all_athletes_info()
