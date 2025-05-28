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
        mock_stage = MagicMock()
        mock_stage.track_url = "http://example.com/track.jpg"
        mock_stage.title = "Test Stage"
        mock_stage.stage_id = 123
        mock_filter.return_value.afirst.return_value = mock_stage

        result = await handler.handle(update, context)

        update.message.reply_photo.assert_called_once()
        assert result == States.MAIN_MENU


@pytest.mark.asyncio
async def test_ggp_subscription_flow():
    handler = GGPSubscriptionHandler()
    update = AsyncMock()
    context = {"user_data": {}}

    with patch(
        "allauth.socialaccount.models.SocialAccount.objects.filter"
    ) as mock_filter:
        mock_account = MagicMock()
        mock_account.user = MagicMock()
        mock_filter.return_value.afirst.return_value = mock_account

        result = await handler.handle(update, context)

        assert result == States.CLASS_SELECTION
        update.message.reply_text.assert_called_with("Выберите класс спортсмена:")
