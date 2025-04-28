from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram_bot"

    def ready(self):
        if not hasattr(self, "bot_started"):
            from django.conf import settings
            from .bot import setup_bot
            import threading

            threading.Thread(target=setup_bot, daemon=True).start()

        self.bot_started = True
