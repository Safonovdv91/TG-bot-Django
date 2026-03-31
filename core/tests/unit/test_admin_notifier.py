import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from users.utils import AdminNotifier


@pytest.mark.asyncio
@pytest.mark.django_db
class TestAdminNotifier:
    """
    Тесты для класса AdminNotifier.

    Проверяют корректность получения контактов администратора
    для уведомления об ошибках и отчетах.
    """

    @patch("users.utils.User.objects.filter")
    async def test_get_admin_contacts_success_returns_username(self, mock_user_filter):
        """
        Администратор найден и имеет username → возвращает @username.

        Проверяет успешный сценарий:
        - Найден суперпользователь в базе
        - У него есть привязанный Telegram-аккаунт
        - В extra_data присутствует username
        """
        # Arrange
        mock_social_account = MagicMock(extra_data={"username": "admin_username"})

        # Создаём mock для socialaccount_set.filter().afirst()
        mock_social_filter = MagicMock()
        mock_social_filter.afirst = AsyncMock(return_value=mock_social_account)

        # Создаём mock администратора с правильным socialaccount_set
        mock_admin = MagicMock()
        mock_admin.socialaccount_set.filter = MagicMock(return_value=mock_social_filter)

        # Настраиваем: User.objects.filter().afirst() → mock_admin
        mock_user_filter.return_value.afirst = AsyncMock(return_value=mock_admin)

        expected_result = "@admin_username"

        # Act
        result = await AdminNotifier.get_admin_contacts()

        # Assert
        assert result == expected_result

    @patch("users.utils.User.objects.filter")
    async def test_get_admin_contacts_admin_exists_no_social_account(
        self, mock_user_filter
    ):
        """
        Администратор найден, но нет Telegram-аккаунта → пустая строка.

        Проверяет сценарий:
        - Суперпользователь существует
        - У него НЕТ привязанного SocialAccount (provider="telegram")
        """
        # Arrange
        # Создаём mock для socialaccount_set.filter().afirst() → None
        mock_social_filter = MagicMock()
        mock_social_filter.afirst = AsyncMock(return_value=None)

        # Создаём mock администратора с socialaccount_set, который возвращает None
        mock_admin = MagicMock()
        mock_admin.socialaccount_set.filter = MagicMock(return_value=mock_social_filter)

        # Настраиваем: User.objects.filter().afirst() → mock_admin
        mock_user_filter.return_value.afirst = AsyncMock(return_value=mock_admin)

        expected_result = ""

        # Act
        result = await AdminNotifier.get_admin_contacts()

        # Assert
        assert result == expected_result

    @pytest.mark.parametrize(
        "username, expected_result",
        [
            ("", ""),
            (None, ""),
        ],
    )
    @patch("users.utils.User.objects.filter")
    async def test_get_admin_contacts_admin_has_no_username_field(
        self, mock_user_filter, username, expected_result
    ):
        """
        Администратор найден, но в extra_data нет username → пустая строка.

        Проверяет сценарий:
        - Социальный аккаунт существует
        - В extra_data отсутствует ключ "username" или он None
        """
        # Arrange
        mock_social_account = MagicMock(extra_data={"username": username})

        # Создаём mock для socialaccount_set.filter().afirst()
        mock_social_filter = MagicMock()
        mock_social_filter.afirst = AsyncMock(return_value=mock_social_account)

        # Создаём mock администратора с правильным socialaccount_set
        mock_admin = MagicMock()
        mock_admin.socialaccount_set.filter = MagicMock(return_value=mock_social_filter)

        # Настраиваем: User.objects.filter().afirst() → mock_admin
        mock_user_filter.return_value.afirst = AsyncMock(return_value=mock_admin)

        # Act
        result = await AdminNotifier.get_admin_contacts()

        # Assert
        assert result == expected_result

    @patch("users.utils.User.objects.filter")
    async def test_get_admin_contacts_no_admin_user_exists(self, mock_user_filter):
        """
        Администратор НЕ найден в базе → пустая строка.

        Проверяет сценарий:
        - В базе нет пользователей с is_superuser=True
        - Метод должен вернуть "" без ошибок
        """
        # Arrange
        mock_admin = None
        mock_user_filter.return_value.afirst = AsyncMock(return_value=mock_admin)

        # Act
        result = await AdminNotifier.get_admin_contacts()

        # Assert
        assert result == ""

    @pytest.mark.parametrize(
        "type_error",
        [Exception("DB error"), ConnectionError("DB error"), TimeoutError("DB error")],
    )
    @patch("users.utils.User.objects.filter")
    async def test_get_admin_contacts_database_error_returns_empty_string(
        self, mock_user_filter, type_error
    ):
        """
        Ошибка базы данных → пустая строка (метод НЕ падает!).

        Проверяет отказоустойчивость:
        - При возникновении исключения в БД
        - Метод должен обработать ошибку и вернуть ""
        - Тест НЕ должен упасть с исключением
        """
        # Arrange
        mock_user_filter.return_value.afirst = AsyncMock(side_effect=type_error)

        # Act
        result = await AdminNotifier.get_admin_contacts()

        # Assert
        assert result == ""
