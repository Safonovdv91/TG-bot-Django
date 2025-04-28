import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from django.conf import settings
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from .models import TelegramUser

User = get_user_model()
logger = logging.getLogger(__name__)


async def create_allauth_user(telegram_user):
    """Асинхронно создает пользователя в django-allauth"""
    email = f"tg_{telegram_user.id}@example.com"
    user = User.objects.create_user(
        username=f"tg_{telegram_user.id}",
        email=email,
        first_name=telegram_user.first_name or "",
        last_name=telegram_user.last_name or "",
    )

    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)

    TelegramUser.objects.get_or_create(
        user=user,
        telegram_id=telegram_user.id,
        defaults={"username": telegram_user.username},
    )
    return user


async def start(update: Update, context):
    """Обработчик команды /start"""
    await handle_message(update, context)


async def handle_message(update: Update, context):
    """Асинхронный обработчик сообщений"""
    tg_user = update.effective_user

    try:
        telegram_user = await TelegramUser.objects.aget(telegram_id=tg_user.id)
        await update.message.reply_text(
            f"Hello @{tg_user.username or tg_user.telegram_id}!"
        )
    except TelegramUser.DoesNotExist:
        user = await create_allauth_user(tg_user)
        await update.message.reply_text(
            f"Вы зарегистрированы как {user.username}!\nТеперь вы можете войти на сайт."
        )


def setup_bot():
    """Настройка и запуск бота"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application
