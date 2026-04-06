import pytest
from unittest.mock import AsyncMock, MagicMock
from django.contrib.auth import get_user_model

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
    message.reply_photo = AsyncMock()  # ← Добавлен AsyncMock для reply_photo
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
