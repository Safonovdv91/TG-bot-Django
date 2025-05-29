import logging

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import Report, SourceReports, TypeReport

User = get_user_model()
logger = logging.getLogger(__name__)


def get_telegram_id(user) -> int | None:
    try:
        social_account = SocialAccount.objects.get(user=user, provider="telegram")
        return social_account.extra_data.get("id")
    except SocialAccount.DoesNotExist:
        return None


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    try:
        social_account = SocialAccount.objects.get(provider="telegram", uid=telegram_id)
        return social_account.user
    except SocialAccount.DoesNotExist:
        return None


class BaseReportValidator:
    """Базовый класс для валидации отчетов"""

    MIN_TEXT_LENGTH = 10

    def __init__(
        self, user: User, text: str, source: str, report_type: TypeReport
    ) -> None:
        self.user = user
        self.text = text
        self.source = source
        self.report_type = None

    def validate(self) -> None:
        errors = []

        if not self.user:
            errors.append("Не указан пользователь")

        if not self.text or len(self.text.strip()) < self.MIN_TEXT_LENGTH:
            errors.append(
                f"Текст отчета слишком короткий (минимум {self.MIN_TEXT_LENGTH} символов)"
            )

        if self.source not in SourceReports.values:
            errors.append("Некорректный источник отчета")

        if errors:
            raise ValidationError(" | ".join(errors))


class ReportCreator:
    """Основной класс для создания отчетов"""

    def __init__(self, validator: BaseReportValidator):
        self.validator = validator

    async def create_report(self, report_type: TypeReport) -> Report:
        """Создание отчета с указанным типом"""
        self.validator.validate()

        return await Report.objects.acreate(
            user=self.validator.user,
            text=self.validator.text.strip(),
            source=self.validator.source,
            report_type=report_type,
        )


class ReportHandler:
    """Обработчик отчетов с дополнительной логикой"""

    @classmethod
    async def handle_report(
        cls, user: User, text: str, source: SourceReports, type_report: TypeReport
    ) -> tuple[bool, str]:
        """Основной метод обработки отчета"""
        validator = BaseReportValidator(user, text, source, type_report)
        creator = ReportCreator(validator)

        try:
            report = await creator.create_report(type_report)
            logger.info(f"Created report: {report.id}")
            return True, "✅ Отчет успешно сохранен!"
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return False, f"❌ Ошибка: {e.message}"
        except Exception as e:
            logger.error(f"Report creation failed: {str(e)}")
            return False, "❌ Произошла непредвиденная ошибка"


class AdminNotifier:
    """Класс для уведомления администраторов"""

    @staticmethod
    async def get_admin_contacts() -> str:
        """Получение контактов администратора"""
        try:
            admin = await User.objects.filter(is_superuser=True).afirst()
            social_account = await admin.socialaccount_set.filter(
                provider="telegram"
            ).afirst()
            return (
                f"@{social_account.extra_data.get('username')}"
                if social_account
                else ""
            )
        except Exception as e:
            logger.error(f"Admin contact error: {str(e)}")
            return ""
