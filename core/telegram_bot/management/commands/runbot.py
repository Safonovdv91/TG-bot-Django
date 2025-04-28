from django.core.management.base import BaseCommand
from telegram_bot.bot import setup_bot


class Command(BaseCommand):
    help = "Запускает Telegram бота"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск бота..."))
        setup_bot()
