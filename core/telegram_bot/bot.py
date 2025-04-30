import logging

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.telegram.provider import TelegramProvider
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from django.conf import settings
from django.contrib.auth import get_user_model

from gymkhanagp.models import UserSubscription

User = get_user_model()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        is_active=True,  # Активируем сразу
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


async def start(update: Update, context):
    """Обработчик команды /start"""
    await handle_message(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_user = update.effective_user
    user, created = await create_user_from_telegram(tg_user)

    if created:
        await update.message.reply_text(
            "🔐 Вы зарегистрированы! "
            "Теперь вы можете войти на сайт, используя Telegram."
        )
    else:
        await update.message.reply_text(f"Привет, {user.first_name}!")


def setup_bot():
    """Настройка и запуск бота"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application
