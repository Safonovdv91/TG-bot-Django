import pytest
from django.core.exceptions import ValidationError

from users.models import SourceReports, TypeReport
from users.utils import BaseReportValidator


@pytest.mark.django_db
class TestBaseReportValidator:
    """Тесты для BaseReportValidator"""

    def test_valid_data_passes_validation(self, django_user):
        """Тест: валидные данные проходят валидацию"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Это достаточно длинный текст для отчета",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act & Assert - не должно быть исключения
        validator.validate()

    def test_missing_user_raises_error(self):
        """Тест: отсутствие пользователя вызывает ошибку"""
        # Arrange
        validator = BaseReportValidator(
            user=None,
            text="Достаточно длинный текст",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "Не указан пользователь" in str(exc_info.value)

    def test_short_text_raises_error(self, django_user):
        """Тест: короткий текст вызывает ошибку"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Короткий",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "слишком короткий" in str(exc_info.value)

    def test_empty_text_raises_error(self, django_user):
        """Тест: пустой текст вызывает ошибку"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "слишком короткий" in str(exc_info.value)

    def test_whitespace_text_raises_error(self, django_user):
        """Тест: текст из пробелов вызывает ошибку"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="   \n\t   ",
            source=SourceReports.TELEGRAM,
            report_type=TypeReport.BUG,
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "слишком короткий" in str(exc_info.value)

    def test_invalid_source_raises_error(self, django_user):
        """Тест: некорректный источник вызывает ошибку"""
        # Arrange
        validator = BaseReportValidator(
            user=django_user,
            text="Достаточно длинный текст для теста",
            source="INVALID_SOURCE",
            report_type=TypeReport.BUG,
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()
        assert "Некорректный источник" in str(exc_info.value)

    def test_multiple_errors_combined(self):
        """Тест: несколько ошибок объединяются"""
        # Arrange
        validator = BaseReportValidator(
            user=None, text="", source="INVALID", report_type=TypeReport.BUG
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate()

        error_message = str(exc_info.value)
        assert "Не указан пользователь" in error_message
        assert "слишком короткий" in error_message
        assert "Некорректный источник" in error_message
        assert " | " in error_message  # Проверяем разделитель
