"""
Configuration file for pytest tests in core/tests/.

Содержит фикстуры и настройку для тестов.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from users.models import Report

User = get_user_model()


# =============================================================================
# Telegram Fixtures
# =============================================================================


@pytest.fixture
def telegram_update():
    """
    Мок объекта Update из python-telegram-bot.
    Не требует базы данных.
    """
    update = MagicMock()
    update.effective_user.id = 123456789
    update.effective_user.first_name = "Test"
    update.effective_user.username = "testuser"

    # Мок сообщения
    message = MagicMock()
    message.text = "Тестовое сообщение"
    message.reply_text = AsyncMock()
    update.message = message

    return update


@pytest.fixture
def telegram_context():
    """
    Мок объекта ContextTypes.DEFAULT_TYPE из python-telegram-bot.
    Не требует базы данных.
    """
    context = MagicMock()
    context.args = []
    context.user_data = {}
    return context


@pytest.fixture
def sample_report_data():
    """Пример данных для отчета"""
    from users.models import TypeReport, SourceReports

    return {
        "text": "Это тестовый отчет о баге в системе",
        "type_report": TypeReport.BUG,
        "source": SourceReports.TELEGRAM,
    }


@pytest.fixture
def mock_register_report():
    """Мок для функции register_report"""
    return AsyncMock(return_value="✅ Отчет успешно сохранен!")


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def django_user(db):
    """
    Создает тестового пользователя Django.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_user(
        username="test_user",
        email="test@example.com",
        password="password1234",
    )
    return user

@pytest_asyncio.fixture
async def django_user_with_telegram(db):
    """
    Создает тестового пользователя Django с telegram.
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    user = await User.objects.acreate_user(
        username="test_user_with_telegram",
        email="test_user_with_telegram@example.com",
        password="password189000981",
    )
    await SocialAccount.objects.acreate(
        user=user, 
        provider="telegram", 
        uid=189000981,
        extra_data={"id": 189000981}  # TG id пользователя
    )
    return user

@pytest_asyncio.fixture(autouse=True)
async def cleanup_db():
    """
    Автоматически очищает БД после каждого теста.
    Используется во всех тестах core/tests/
    """
    yield
    await Report.objects.all().adelete()
    await User.objects.all().adelete()
    await SocialAccount.objects.all().adelete()
