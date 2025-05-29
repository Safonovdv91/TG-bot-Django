import pytest

from django.core.exceptions import ValidationError

from users.models import SourceReports, TypeReport, Report
from users.utils import ReportHandler, BaseReportValidator, ReportCreator


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
class TestReportHandler:
    """Тесты для ReportHandler"""

    async def test_handle_report_success(self, django_user):
        """Тест: успешная обработка отчета"""
        # Act
        success, message = await ReportHandler.handle_report(
            user=django_user,
            text="Достаточно длинный текст для отчета о проблеме",
            source=SourceReports.TELEGRAM,
            type_report=TypeReport.BUG,
        )

        # Assert
        assert success is True
        assert message == "✅ Отчет успешно сохранен!"

        # Проверяем, что отчет создался в базе
        report = await Report.objects.aget()
        assert report.user == django_user
        assert report.text == "Достаточно длинный текст для отчета о проблеме"
        assert report.source == SourceReports.TELEGRAM
        assert report.report_type == TypeReport.BUG

    async def test_handle_report_validation_error(self, django_user):
        """Тест: ошибка валидации"""
        # Act
        success, message = await ReportHandler.handle_report(
            user=django_user,
            text="Короткий",  # слишком короткий текст
            source=SourceReports.TELEGRAM,
            type_report=TypeReport.BUG,
        )

        # Assert
        assert success is False
        assert "❌ Ошибка:" in message
        assert "слишком короткий" in message

        # Проверяем, что отчет НЕ создался
        reports_count = await Report.objects.acount()
        assert reports_count == 0


@pytest.mark.django_db
@pytest.mark.asyncio
class TestReportCreator:
    """Тесты для ReportCreator"""

    async def test_init_with_validator(self, django_user):
        """Тест: инициализация с валидатором"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Текст отчета достаточной длины",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act
        creator = ReportCreator(validator)

        # Assert
        assert creator.validator == validator

    async def test_create_report_success(self, django_user):
        """Тест: успешное создание отчета"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Текст отчета достаточной длины для теста",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )
        creator = ReportCreator(validator)

        # Act
        report = await creator.create_report(TypeReport.BUG)

        # Assert
        assert isinstance(report, Report)
        assert report.user == django_user
        assert report.text == "Текст отчета достаточной длины для теста"
        assert report.source == SourceReports.TELEGRAM
        assert report.report_type == TypeReport.BUG

    async def test_create_report_validation_fails(self, django_user):
        """Тест: создание отчета с ошибкой валидации"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Короткий",  # слишком короткий
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )
        creator = ReportCreator(validator)

        # Act & Assert
        with pytest.raises(ValidationError):
            await creator.create_report(TypeReport.BUG)

    async def test_create_report_strips_whitespace(self, django_user):
        """Тест: создание отчета обрезает пробелы"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="  Текст отчета с пробелами в начале и конце  ",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )
        creator = ReportCreator(validator)

        # Act
        report = await creator.create_report(TypeReport.BUG)

        # Assert
        assert report.text == "Текст отчета с пробелами в начале и конце"
