import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_telegram_user_subscription(sender, instance, created, **kwargs):
    """
    Сигнал для создания модели подписки при регистрации пользователя.
    """
    if created:
        logger.info("Создана подписка для пользователя %s", instance.username)
        UserSubscription.objects.create(
            user=instance,
        )
