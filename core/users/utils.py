from __future__ import annotations

import logging

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from gymkhanagp.tasks import send_telegram_message_task
from users.models import Report, SourceReports, TypeReport

User = get_user_model()
logger = logging.getLogger(__name__)


def get_telegram_id(user: AbstractBaseUser) -> int | None:
    if type(user) is not User:
        logger.error(
            "Запрос пользователя который не User:\n %s \ntype: [%s]", user, type(user)
        )
        return None

    try:
        social_account = SocialAccount.objects.get(user=user, provider="telegram")
        return social_account.extra_data.get("id")
    except SocialAccount.DoesNotExist:
        return None


def get_user_by_telegram_id(telegram_id: int | str | None) -> AbstractBaseUser | None:
    if telegram_id is None:
        return None

    if type(telegram_id) not in (int, str):
        logger.error("Получено неверное значение telegram_id: %s", telegram_id)
        return None

    try:
        tg_id = int(telegram_id)
        social_account = SocialAccount.objects.get(provider="telegram", uid=tg_id)
        return social_account.user
    except SocialAccount.DoesNotExist:
        return None
    except ValueError:
        return None


class BaseReportValidator:
    """Базовый класс для валидации отчетов"""

    MIN_TEXT_LENGTH = 10

    def __init__(
        self, user: AbstractBaseUser, text: str, source: str, report_type: TypeReport
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
        cls,
        user: AbstractBaseUser,
        text: str,
        source: SourceReports,
        type_report: TypeReport,
    ) -> tuple[bool, str]:
        """Основной метод обработки отчета"""
        validator = BaseReportValidator(user, text, source, type_report)
        creator = ReportCreator(validator)

        try:
            report: Report = await creator.create_report(type_report)
            logger.info(f"Created report: {report.pk}")
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

            if admin is None:
                return ""

            social_account = await admin.socialaccount_set.filter(
                provider="telegram"
            ).afirst()
            result = social_account.extra_data.get("username")

            return f"@{result}" if result else ""
        except ConnectionError:
            logger.exception("Получена ошибка подключения к базе данных")
            return ""
        except Exception as e:
            logger.error(f"Admin contact error: {str(e)}")
            return ""

    @staticmethod
    def notify_admin(message: str) -> bool:
        """
        Отправка уведомления администратору через Celery.

        Аргументы:
        - message: Текст сообщения для отправки

        Возвращает:
        - bool: True если задача успешно отправлена, False иначе

        """
        try:
            user = User.objects.filter(
                is_superuser=True, is_active=True, socialaccount__provider="telegram"
            ).first()
        except Exception as e:
            logger.exception(
                "Ошибка получения администратора из базы данных", exc_info=e
            )
            return False

        if user is None:
            logger.error(
                "При отправке уведомления администратору через telegramm"
                " администратор c телеграмм не был обнаружен в БД"
            )
            return False

        telegram_id: int | None = get_telegram_id(user)

        try:
            send_telegram_message_task.delay(telegram_id, message)
        except Exception as e:
            logger.exception(
                "При создании таски по уведомлению пользователя было вызвано исключение:",
                exc_info=e,
            )
            return False

        logger.info("Администратоу выслано сообщение: %s", message)
        return True
