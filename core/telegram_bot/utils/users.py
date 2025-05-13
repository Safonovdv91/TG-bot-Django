from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.telegram.provider import TelegramProvider
from django.contrib.auth import get_user_model
from gymkhanagp.models import UserSubscription

User = get_user_model()


async def create_user_from_telegram(tg_user) -> (User, bool):
    """Создаёт или возвращает пользователя Django + SocialAccount."""
    # Проверяем, есть ли SocialAccount с этим telegram_id
    social_account = await SocialAccount.objects.filter(uid=str(tg_user.id)).afirst()

    if social_account:
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

    await UserSubscription.objects.acreate(
        user=user,
        is_active=True,
        source="telegram",
    )

    return user, True
