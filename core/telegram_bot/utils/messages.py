import os
import logging

from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from telegram import Bot
from django.contrib.auth import get_user_model
from telegram.error import Forbidden

from telegram_bot.utils.math_calculate import TimeConverter

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


class MessageTimeTableFormatter:
    def __init__(self, time_converter: TimeConverter):
        self.time_converter = time_converter
        self.class_ranges = [
            ("🟦 🇧", 1.00, 1.05),
            ("🟩 С1", 1.05, 1.10),
            ("🟩 С2", 1.10, 1.15),
            ("🟩 С3", 1.15, 1.20),
            ("🟨 D1", 1.20, 1.30),
            ("🟨 D2", 1.30, 1.40),
            ("🟨 D3", 1.40, 1.50),
            ("🟨 D4", 1.50, 1.60),
        ]

    def format_time_ranges(self, base_time: int) -> str:
        lines = []
        for emoji, start, end in self.class_ranges:
            start_time = self.time_converter.to_mmssms(int(base_time * start))
            end_time = self.time_converter.to_mmssms(int(base_time * end - 1))
            lines.append(f"{emoji}: {start_time} - {end_time}")
        return "\n".join(lines)
