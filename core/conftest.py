import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes
from users.models import Report

User = get_user_model()


def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def django_user():
    """Создает тестового пользователя Django"""

    user = await User.objects.acreate_user(  # type: ignore
        username="test_user",
        email="test@example.com",
        password="password1234",
    )
    await SocialAccount.objects.acreate(user=user, provider="telegram", uid=123456789)
    return user


@pytest.fixture
def telegram_user():
    """Создает мок Telegram пользователя"""
    return TelegramUser(
        id=123456789,
        first_name="Test",
        last_name="User",
        username="testuser",
        is_bot=False,
    )


@pytest.fixture
def telegram_chat():
    """Создает мок Telegram чата"""
    return Chat(id=123456789, type=Chat.PRIVATE, title="Test Chat")


@pytest.fixture
def telegram_message(telegram_user, telegram_chat):
    """Создает мок Telegram сообщения"""
    message = MagicMock(spec=Message)
    message.from_user = telegram_user
    message.chat = telegram_chat
    message.message_id = 1
    message.date = None
    message.text = "Test message"
    message.reply_text = AsyncMock()
    return message


@pytest.fixture
def telegram_update(telegram_message, telegram_user):
    """Создает мок Telegram Update"""
    update = MagicMock(spec=Update)
    update.message = telegram_message
    update.effective_user = telegram_user
    update.effective_chat = telegram_message.chat
    return update


@pytest.fixture
def telegram_context():
    """Создает мок Telegram Context"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = []
    context.user_data = {}
    return context


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    """Автоматически очищает БД после каждого теста"""
    yield
    await Report.objects.all().adelete()
    await User.objects.all().adelete()
    await SocialAccount.objects.all().adelete()
