import logging

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

from telegram_bot.manager import KeyboardManager

User = get_user_model()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard_manager = KeyboardManager()
    await keyboard_manager._handle_regular_message(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard_manager = KeyboardManager()
    await keyboard_manager.handle_message(update, context)


def setup_bot():
    """Настройка и запуск бота"""
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return application
