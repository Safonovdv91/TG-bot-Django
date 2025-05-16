import logging

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.telegram.provider import TelegramProvider
from django.contrib.auth import get_user_model
from gymkhanagp.models import UserSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


async def create_user_from_telegram(tg_user) -> (User, bool):
    """Создаёт или возвращает пользователя Django + SocialAccount."""
    # Проверяем, есть ли SocialAccount с этим telegram_id
    logger.info(f"Создаем пользователя через телеграмм: {tg_user}")
    social_account = await SocialAccount.objects.filter(uid=str(tg_user.id)).afirst()

    if social_account:
        logger.info(f"Найден существующий пользователь через телеграмм: {tg_user}")
        return social_account.user, False

    # Создаём пользователя Django
    user = await User.objects.acreate(
        username=f"tg_{tg_user.id}",
        first_name=tg_user.first_name or "",
        last_name=tg_user.last_name or "",
        is_active=True,
    )

    # Создаём SocialAccount
    await SocialAccount.objects.acreate(
        user=user,
        provider=TelegramProvider.id,
        uid=str(tg_user.id),
        extra_data={
            "id": tg_user.id,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
            "username": tg_user.username,
        },
    )

    user_subscription = await UserSubscription.objects.filter(user=user).afirst()
    if user_subscription:
        user_subscription.source = "telegram"
        user_subscription.save()

    logger.info(f"Создан новый пользователь через телеграмм: {tg_user}")

    return user, True
