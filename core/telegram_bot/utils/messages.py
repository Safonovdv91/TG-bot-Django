from __future__ import annotations

import logging
import os

from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from telegram import Bot
from telegram.error import Forbidden
from telegram_bot.utils.math_calculate import TimeConverter

User = get_user_model()
logger = logging.getLogger(__name__)


TOKEN: str | None = getattr(
    settings, "TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN")
)

if TOKEN is None:
    raise ValueError(
        "Token для бота не установлен, пожалуйста установите TOKEN для бота в .env"
    )


@sync_to_async
def get_user_by_tg_id(tg_id: int) -> AbstractBaseUser | None:
    tg_user = SocialAccount.objects.filter(provider="telegram", uid=tg_id).first()
    if tg_user is None:
        logger.error("У пользователя отсутствует аккаунт телеграмм")
        return None

    user = tg_user.user
    return user


async def send_telegram_message(chat_id: int, text: str) -> bool:
    if TOKEN is None:
        raise ValueError(
            "Token для бота не установлен, пожалуйста установите TOKEN для бота в .env"
        )

    bot = Bot(token=TOKEN)
    logger.info("[%s]: %s", chat_id, text)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except Forbidden:
        logger.info(
            "[%s]: Пользователь заблокировал, переводим его в неактивного", chat_id
        )
        user: AbstractBaseUser | None = await get_user_by_tg_id(chat_id)
        if user is None:
            logger.error(
                "Сообщение пользователю не выслано, т.к. найденный пользователь us None"
            )
            return False
        user.is_active = False
        user.save()
    except Exception as e:
        logger.error(f"Telegram send error: {e}", exc_info=True)

    return True


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
