import pytest
from unittest.mock import patch

from users.utils import AdminNotifier


@pytest.mark.django_db
class TestAdminNotifierNotifyAdmin:
    """
    Тесты для метода AdminNotifier.notify_admin().

    Проверяют корректность отправки уведомлений администратору
    через Celery задачу.
    """

    @patch("users.utils.send_telegram_message_task")
    @pytest.mark.asyncio
    async def test_notify_admin_success_sends_message(
        self, mock_send_task, django_admin_with_telegram
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
        # django_admin_with_telegram — это фикстура, pytest-asyncio сам обрабатывает await
        django_admin_with_telegram

        # Act
        result = AdminNotifier.notify_admin("Test message for admin")

        # Assert
        assert result is True
        mock_send_task.delay.assert_called_once_with(
            666666666, "Test message for admin"
        )

    # @patch("users.utils.send_telegram_message_task")
    # @patch("users.utils.get_telegram_id")
    # def test_notify_admin_no_telegram_account(
    #     self, mock_get_tg_id, mock_send_task, django_user
    # ):
    #     """
    #     У администратора нет Telegram аккаунта → возвращает False.

    #     Проверяет сценарий:
    #     - Администратор существует
    #     - У администратора НЕТ Telegram ID (get_telegram_id возвращает None)
    #     - Celery задача НЕ вызывается
    #     - Метод возвращает False
    #     """
    #     # Arrange
    #     # TODO: Создай администратора
    #     # TODO: Настрой mock_get_tg_id.return_value = None

    #     # Act
    #     # TODO: Вызови AdminNotifier.notify_admin("Test message")

    #     # Assert
    #     # TODO: Проверь, что результат == False
    #     # TODO: Проверь, что mock_send_task.delay НЕ вызывался
    #     pass

    # @patch("users.utils.send_telegram_message_task")
    # @patch("users.utils.get_telegram_id")
    # def test_notify_admin_user_not_active(
    #     self, mock_get_tg_id, mock_send_task, django_user
    # ):
    #     """
    #     Администратор не активен → возвращает False.

    #     Проверяет сценарий:
    #     - Администратор существует
    #     - Администратор НЕ активен (is_active=False)
    #     - Celery задача НЕ вызывается
    #     - Метод возвращает False
    #     """
    #     # Arrange
    #     # TODO: Создай администратора с is_active=False
    #     # TODO: Настрой mock_get_tg_id.return_value = 123456789

    #     # Act
    #     # TODO: Вызови AdminNotifier.notify_admin("Test message")

    #     # Assert
    #     # TODO: Проверь, что результат == False
    #     # TODO: Проверь, что mock_send_task.delay НЕ вызывался
    #     pass

    # @patch("users.utils.send_telegram_message_task")
    # def test_notify_admin_no_admin_exists(
    #     self, mock_send_task
    # ):
    #     """
    #     В базе нет администратора → возвращает False.

    #     Проверяет сценарий:
    #     - В базе НЕТ пользователей с is_superuser=True
    #     - Celery задача НЕ вызывается
    #     - Метод возвращает False
    #     """
    #     # Arrange
    #     # TODO: Не создавай администратора в базе

    #     # Act
    #     # TODO: Вызови AdminNotifier.notify_admin("Test message")

    #     # Assert
    #     # TODO: Проверь, что результат == False
    #     # TODO: Проверь, что mock_send_task.delay НЕ вызывался
    #     pass

    # @patch("users.utils.send_telegram_message_task")
    # @patch("users.utils.get_telegram_id")
    # def test_notify_admin_celery_task_error(
    #     self, mock_get_tg_id, mock_send_task, django_user
    # ):
    #     """
    #     Ошибка при отправке Celery задачи → возвращает False.

    #     Проверяет сценарий:
    #     - Администратор существует и активен
    #     - Telegram ID существует
    #     - При вызове send_telegram_message_task.delay() возникает исключение
    #     - Метод возвращает False (не падает!)
    #     """
    #     # Arrange
    #     # TODO: Создай администратора
    #     # TODO: Настрой mock_get_tg_id.return_value = 123456789
    #     # TODO: Настрой mock_send_task.delay.side_effect = Exception("Celery error")

    #     # Act
    #     # TODO: Вызови AdminNotifier.notify_admin("Test message")

    #     # Assert
    #     # TODO: Проверь, что результат == False
    #     # TODO: Проверь, что метод НЕ упал с исключением
    #     pass

    # @patch("users.utils.send_telegram_message_task")
    # @patch("users.utils.get_telegram_id")
    # def test_notify_admin_database_error(
    #     self, mock_get_tg_id, mock_send_task, django_user
    # ):
    #     """
    #     Ошибка базы данных при получении администратора → возвращает False.

    #     Проверяет сценарий:
    #     - При запросе администратора возникает DatabaseError
    #     - Метод возвращает False (не падает!)
    #     """
    #     # Arrange
    #     # TODO: Настрой ошибку БД при получении администратора
    #     # TODO: Используй patch для User.objects.filter

    #     # Act
    #     # TODO: Вызови AdminNotifier.notify_admin("Test message")

    #     # Assert
    #     # TODO: Проверь, что результат == False
    #     # TODO: Проверь, что метод НЕ упал с исключением
    #     pass

    # # TODO: Подумай, какие ещё сценарии стоит протестировать
    # # Например:
    # # - Сообщение пустое или None
    # # - Сообщение очень длинное
    # # - Несколько администраторов в базе (какой выбирается?)
