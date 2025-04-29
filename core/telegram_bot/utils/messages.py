import os
import logging

from asgiref.sync import sync_to_async
from telegram import Bot
from django.contrib.auth import get_user_model

User = get_user_model()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger = logging.getLogger(__name__)


@sync_to_async
def get_user_by_tg_id(tg_id: int) -> User:
    return User.objects.filter(username=f"tg_{tg_id}").first()


async def send_telegram_message(chat_id: int, text: str):
    try:
        bot = Bot(token=TOKEN)
        logger.info("[%s]: %s", chat_id, text)
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error(f"Telegram send error: {e}", exc_info=True)
