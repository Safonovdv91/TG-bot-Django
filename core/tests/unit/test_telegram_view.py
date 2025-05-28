import pytest
from unittest.mock import patch

from telegram_bot.commands import bug_report, register_report
from users.models import TypeReport, SourceReports
from telegram_bot.states import States


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
class TestBugReportView:
    """Тесты для команды /bug_report"""

    async def test_bug_report_without_args_requests_input(
        self, telegram_update, telegram_context
    ):
        """Тест: без аргументов запрашивает ввод текста"""
        # Arrange
        telegram_context.args = None

        # Act
        result = await bug_report(telegram_update, telegram_context)

        # Assert
        telegram_update.message.reply_text.assert_called_once_with(
            "Опишите пожалуйста проблему в одном сообщении:"
        )
        assert telegram_context.user_data["state"] == States.BUG_REPORT_WAIT
        assert result == States.BUG_REPORT_WAIT

    async def test_bug_report_with_empty_args_requests_input(
        self, telegram_update, telegram_context
    ):
        """Тест: с пустыми аргументами запрашивает ввод"""
        # Arrange
        telegram_context.args = []

        # Act
        result = await bug_report(telegram_update, telegram_context)

        # Assert
        telegram_update.message.reply_text.assert_called_once_with(
            "Опишите пожалуйста проблему в одном сообщении:"
        )
        assert result == States.BUG_REPORT_WAIT

    @patch("telegram_bot.commands.register_report")
    async def test_bug_report_with_args_creates_report(
        self, mock_register_report, telegram_update, telegram_context
    ):
        """Тест: с аргументами создает отчет"""
        # Arrange
        telegram_context.args = ["Ошибка", "в", "системе"]
        mock_register_report.return_value = "✅ Отчет создан!"

        # Act
        result = await bug_report(telegram_update, telegram_context)

        # Assert
        mock_register_report.assert_called_once_with(
            telegram_id=123456789, text="Ошибка в системе", type_report=TypeReport.BUG
        )
        telegram_update.message.reply_text.assert_called_once_with("✅ Отчет создан!")
        assert telegram_context.user_data["state"] == States.MAIN_MENU
        assert result == States.MAIN_MENU


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
class TestRegisterReport:
    """Тесты для функции register_report"""

    @patch("users.utils.get_user_by_telegram_id")
    @patch("users.utils.ReportHandler.handle_report")
    async def test_register_report_success(
        self, mock_handle_report, mock_get_user, django_user
    ):
        """Тест: успешная регистрация отчета"""
        # Arrange
        mock_get_user.return_value = django_user
        mock_handle_report.return_value = (True, "✅ Отчет сохранен!")

        # Act
        result = await register_report(
            telegram_id=123456789, text="Тестовый отчет", type_report=TypeReport.BUG
        )

        # Assert
        mock_handle_report.assert_called_once_with(
            user=django_user,
            text="Тестовый отчет",
            source=SourceReports.TELEGRAM,
            type_report=TypeReport.BUG,
        )
        assert result == "✅ Отчет сохранен!"

    @patch("users.utils.get_user_by_telegram_id")
    @patch("telegram_bot.keyboard.ReportHandler.handle_report")
    @patch("users.utils.AdminNotifier.get_admin_contacts")
    async def test_register_report_failure_adds_admin_contact(
        self, mock_get_admin, mock_handle_report, mock_get_user, django_user
    ):
        """Тест: при ошибке добавляет контакт админа"""
        # Arrange
        mock_get_user.return_value = django_user
        mock_handle_report.return_value = (False, "❌ Ошибка валидации")
        mock_get_admin.return_value = "@admin"

        # Act
        result = await register_report(
            telegram_id=123456789, text="Короткий текст", type_report=TypeReport.BUG
        )

        # Assert
        expected = "❌ Ошибка валидации\nСвяжитесь с администратором: @admin"
        assert result == expected
        mock_get_admin.assert_called_once()
