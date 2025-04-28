from telegram.ext import Updater, CommandHandler, MessageHandler
from django.conf import settings
from django.contrib.auth.models import User
import logging

from .models import TelegramUser

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update, context):
    """Обработчик команды /start"""
    telegram_user = update.effective_user
    user, created = get_or_create_django_user(telegram_user)

    if created:
        update.message.reply_text(
            f"Вы успешно добавлены в систему как {user.username}!"
        )
    else:
        update.message.reply_text(f"Привет, @{telegram_user.username}!")


def handle_message(update, context):
    """Обработчик всех сообщений"""
    telegram_user = update.effective_user
    user, created = get_or_create_django_user(telegram_user)

    if created:
        update.message.reply_text(f"Добро пожаловать, {user.first_name}!")
    else:
        update.message.reply_text(f"Вы уже в системе, @{telegram_user.username}!")


def get_or_create_django_user(telegram_user):
    """Создает или получает пользователя Django"""
    try:
        tg_user = TelegramUser.objects.get(telegram_id=telegram_user.id)
        return tg_user.user, False
    except TelegramUser.DoesNotExist:
        # Создаем пользователя Django
        user = User.objects.create_user(
            username=f"tg_{telegram_user.id}",
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )

        # Создаем запись TelegramUser
        TelegramUser.objects.create(
            user=user,
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        return user, True


def setup_bot():
    """Настройка и запуск бота"""
    updater = Updater(settings.TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))

    # Обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запуск бота
    updater.start_polling()
    updater.idle()
