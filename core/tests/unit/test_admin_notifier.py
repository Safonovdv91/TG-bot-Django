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
    async def test_get_admin_contacts_success_returns_username(
        self, mock_user_filter
    ):
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

