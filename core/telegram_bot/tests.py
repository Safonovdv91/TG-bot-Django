import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram_bot.keyboard import TrackHandler, GGPSubscriptionHandler
from telegram_bot.states import States


@pytest.mark.asyncio
async def test_track_handler_success():
    handler = TrackHandler()
    update = AsyncMock()
    context = AsyncMock()

    with patch("g_cup_site.models.StageModel.objects.filter") as mock_filter:
        mock_query = AsyncMock()
        mock_stage = MagicMock()
        mock_stage.track_url = "http://example.com/track.jpg"
        mock_stage.title = "Test Stage"
        mock_stage.stage_id = 123
        mock_query.afirst.return_value = mock_stage
        mock_filter.return_value = mock_query

        result = await handler.handle(update, context)

        update.message.reply_photo.assert_called_once()
        assert result == States.MAIN_MENU


@pytest.mark.asyncio
async def test_ggp_subscription_flow():
    handler = GGPSubscriptionHandler()
    update = AsyncMock()
    context = AsyncMock()
    context.user_data = {}

    # Настроим моки для эффективного пользователя
    user_mock = MagicMock()
    user_mock.id = 12345
    update.effective_user = user_mock

    with patch(
        "allauth.socialaccount.models.SocialAccount.objects.filter"
    ) as mock_filter:
        mock_query = AsyncMock()
        mock_account = MagicMock()
        mock_account.user = MagicMock()
        mock_query.afirst.return_value = mock_account
        mock_filter.return_value = mock_query

        async def async_get_or_create(*args, **kwargs):
            mock_subscription = MagicMock()
            mock_subscription.id = 1
            return (mock_subscription, True)  # (instance, created)

        with patch(
            "gymkhanagp.models.UserSubscription.objects.aget_or_create",
            side_effect=async_get_or_create,
        ):
            # Замокаем _get_user_subscriptions
            with patch.object(handler, "_get_user_subscriptions", return_value=[]):
                # Замокаем get_keyboard
                with patch.object(handler, "get_keyboard", return_value=[["🔙 Назад"]]):
                    result = await handler.handle(update, context)

                    assert result == States.CLASS_SELECTION
                    update.message.reply_text.assert_called_once()
                    # Проверяем, что был вызван reply_text с нужным текстом
                    args, kwargs = update.message.reply_text.call_args
                    assert "Выберите класс спортсмена:" in args[0]
