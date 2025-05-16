import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class GymkhanagpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gymkhanagp"

    def ready(self):
        from . import signals

        logger.debug(
            f"Импортированы signals {signals.create_telegram_user_subscription}"
        )
