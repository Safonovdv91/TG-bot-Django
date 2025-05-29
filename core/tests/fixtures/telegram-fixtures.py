import pytest
from unittest.mock import AsyncMock
from users.models import Report, TypeReport, SourceReports


@pytest.fixture
def mock_register_report():
    """Мок для функции register_report"""
    return AsyncMock(return_value="✅ Отчет успешно сохранен!")


@pytest.fixture
def sample_report_data():
    """Пример данных для отчета"""
    return {
        "text": "Это тестовый отчет о баге в системе",
        "type_report": TypeReport.BUG,
        "source": SourceReports.TELEGRAM,
    }


@pytest.fixture
def created_report(django_user, sample_report_data):
    """Созданный отчет в базе данных"""
    return Report.objects.create(
        user=django_user,
        text=sample_report_data["text"],
        source=sample_report_data["source"],
        report_type=sample_report_data["type_report"],
    )
