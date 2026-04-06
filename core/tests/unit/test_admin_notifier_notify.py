import pytest
from unittest.mock import patch, MagicMock

from users.utils import AdminNotifier


@pytest.mark.django_db
class TestAdminNotifierNotifyAdmin:
    """
    Тесты для метода AdminNotifier.notify_admin().

    Проверяют корректность отправки уведомлений администратору
    через Celery задачу.
    """

    @pytest.mark.parametrize(
        "test_message", ["", "Good message", 10000 * "Very Big Message!!\n", None]
    )
    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_success_sends_message(
        self, mock_send_task, django_admin_with_telegram, test_message
    ):
        """
        Администратор найден и активен → задача отправлена в Celery.

        Проверяет сценарий:
        - Администратор существует в базе (is_superuser=True)
        - Администратор активен (is_active=True)
        - У администратора есть Telegram ID
        - Celery задача успешно отправляется
        - Метод возвращает True
        """
        # Arrange

        # Act
        result = AdminNotifier.notify_admin(test_message)

        # Assert
        assert result is True
        mock_send_task.delay.assert_called_once_with(666666666, test_message)

    @patch("users.utils.logger")
    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_no_telegram_account(
        self, mock_send_task, mock_logger, django_superuser
    ):
        """
        У администратора нет Telegram аккаунта → возвращает False.

        Проверяет сценарий:
        - Администратор существует
        - У администратора НЕТ Telegram ID
        - Celery задача НЕ вызывается
        - Метод возвращает False
        """
        # Arrange

        # Act
        result = AdminNotifier.notify_admin("Test message")

        # Assert

        mock_send_task.delay.assert_not_called()
        mock_logger.error.assert_called_once()
        assert not result

    @patch("users.utils.logger")
    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_user_not_active(
        self, mock_send_task, mock_logger, django_admin_with_telegram_not_active
    ):
        """
        Администратор не активен → возвращает False.

        Проверяет сценарий:
        - Администратор существует
        - Администратор НЕ активен (is_active=False)
        - Celery задача НЕ вызывается
        - Метод возвращает False
        """
        # Arrange

        # Act
        result = AdminNotifier.notify_admin("Test message")

        # Assert
        assert not result
        mock_logger.error.assert_called_once()
        mock_send_task.delay.assert_not_called()

    @patch("users.utils.logger")
    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_no_admin_exists(
        self, mock_send_task, mock_logger, django_user
    ):
        """
        В базе нет администратора → возвращает False.

        Проверяет сценарий:
        - В базе НЕТ пользователей с is_superuser=True
        - Celery задача НЕ вызывается
        - Метод возвращает False
        """
        # Arrange

        # Act
        result = AdminNotifier.notify_admin("Test message")

        # Assert
        assert not result
        mock_logger.error.assert_called_once()
        mock_send_task.delay.assert_not_called()

    @pytest.mark.parametrize(
        "type_error",
        [Exception("DB error"), ConnectionError("DB error"), TimeoutError("DB error")],
    )
    @patch("users.utils.logger")
    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_celery_task_error(
        self, mock_send_task, mock_logger, django_admin_with_telegram, type_error
    ):
        """
        Ошибка при отправке Celery задачи → возвращает False.

        Проверяет сценарий:
        - Администратор существует и активен
        - Telegram ID существует
        - При вызове send_telegram_message_task.delay() возникает исключение
        - Метод возвращает False (не падает!)
        """
        # Arrange
        mock_send_task.delay.side_effect = type_error

        # Act
        result = AdminNotifier.notify_admin("Test message")

        # Assert
        assert not result
        mock_logger.exception.assert_called_once()

    @pytest.mark.parametrize(
        "type_error",
        [Exception("DB error"), ConnectionError("DB error"), TimeoutError("DB error")],
    )
    @patch("users.utils.logger")
    @patch("users.utils.User.objects.filter")
    async def test_notify_admin_database_error(
        self, mock_user_filter, mock_logger, django_admin_with_telegram, type_error
    ):
        """
        Ошибка базы данных при получении администратора → возвращает False.

        Проверяет сценарий:
        - При запросе администратора возникает DatabaseError
        - Метод возвращает False (не падает!)
        """
        # Arrange
        mock_user_filter.return_value.first = MagicMock(side_effect=type_error)

        # Act
        result = AdminNotifier.notify_admin("Test message")

        # Assert
        assert not result
        mock_logger.exception.assert_called_once()
