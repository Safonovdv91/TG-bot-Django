import os
import logging

from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from telegram import Bot
from django.contrib.auth import get_user_model
from telegram.error import Forbidden

User = get_user_model()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger = logging.getLogger(__name__)


@sync_to_async
def get_user_by_tg_id(tg_id: int) -> User:
    tg_user = SocialAccount.objects.filter(provider="telegram", uid=tg_id).first()
    user = tg_user.user
    return user


async def send_telegram_message(chat_id: int, text: str):
    try:
        bot = Bot(token=TOKEN)
        logger.info("[%s]: %s", chat_id, text)
        await bot.send_message(chat_id=chat_id, text=text)
    except Forbidden:
        logger.info(
            "[%s]: Пользователь заблокировал, переводим его в неактивного", chat_id
        )
        user: User = await get_user_by_tg_id(chat_id)
        user.is_active = False
        user.save()
    except Exception as e:
        logger.error(f"Telegram send error: {e}", exc_info=True)
