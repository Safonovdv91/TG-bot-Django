import asyncio
from django.core.management.base import BaseCommand
from telegram_bot.bot import setup_bot


class Command(BaseCommand):
    help = "Запускает Telegram бота"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting bot..."))
        application = setup_bot()

        # Для Django 4.1+ с поддержкой async
        async def run():
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            await asyncio.Event().wait()  # Бесконечное ожидание

        asyncio.run(run())
