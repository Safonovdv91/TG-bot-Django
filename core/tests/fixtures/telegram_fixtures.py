"""
Telegram fixtures для тестов.

Содержит фикстуры для тестирования telegram_bot.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from django.contrib.auth import get_user_model
from users.models import Report, TypeReport, SourceReports


@pytest.fixture
def sample_report_data():
    """Пример данных для отчета"""
    return {
        "text": "Это тестовый отчет о баге в системе",
        "type_report": TypeReport.BUG,
        "source": SourceReports.TELEGRAM,
    }


@pytest.fixture
def mock_register_report():
    """Мок для функции register_report"""
    return AsyncMock(return_value="✅ Отчет успешно сохранен!")


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
def django_user(db):
    """
    Создает тестового пользователя Django.
    
    Требует базу данных (используйте @pytest.mark.django_db).
    """
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    return user


@pytest.fixture
def created_report(django_user, sample_report_data):
    """
    Созданный отчет в базе данных.
    
    Требует базу данных и пользователя.
    """
    return Report.objects.create(
        user=django_user,
        text=sample_report_data["text"],
        source=sample_report_data["source"],
        report_type=sample_report_data["type_report"],
    )
