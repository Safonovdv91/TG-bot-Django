import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from django.db import DatabaseError, IntegrityError, DataError


from telegram_bot.keyboard import TrackHandler
from telegram_bot.states import States



@pytest.mark.asyncio
@pytest.mark.django_db
class TestTrackHandler:
    """
    Тесты для TrackHandler.

    Проверяют корректность обработки команды отправки карты этапа.
    """

    @patch("telegram_bot.keyboard.StageModel.objects.filter")
    async def test_handle_stage_found_sends_photo(
        self, mock_stage_filter, telegram_update, telegram_context
    ):
        """
        Stage найден → отправляет фото трека и возвращает States.MAIN_MENU.

        Проверяет сценарий:
        - Найден активный этап со статусом "judging" или "accepting"
        - У этапа есть track_url
        - Отправляется фото с caption
        - Возвращается States.MAIN_MENU
        """
        # Arrange
        mock_stage = MagicMock()
        mock_stage.track_url = "http://example.com/track.jpg"
        mock_stage.title = "Test Stage"
        mock_stage.stage_id = 123

        mock_stage_filter.return_value.afirst = AsyncMock(return_value=mock_stage)
        telegram_update.message.reply_photo = AsyncMock()

        handler = TrackHandler()

        # Act
        result = await handler.handle(telegram_update, telegram_context)

        # Assert
        assert result == States.MAIN_MENU
        telegram_update.message.reply_photo.assert_called_once()
        call_args = telegram_update.message.reply_photo.call_args
        assert call_args.kwargs["photo"] == mock_stage.track_url  # Проверка URL
        assert "Test Stage" in call_args.kwargs["caption"]  # Проверка caption
        assert "gymkhana-cup.ru" in call_args.kwargs["caption"]  # Проверка ссылки

    @patch("telegram_bot.keyboard.StageModel.objects.filter")
    async def test_handle_stage_not_found_sends_text(
        self, mock_stage_filter, telegram_update, telegram_context
    ):
        """
        Stage НЕ найден → отправляет сообщение и возвращает States.MAIN_MENU.

        Проверяет сценарий:
        - Нет активных этапов (afirst возвращает None)
        - Отправляется текстовое сообщение "Нет активных соревнований"
        - Возвращается States.MAIN_MENU
        """
        # Arrange
        mock_stage_filter.return_value.afirst = AsyncMock(return_value=None)

        handler = TrackHandler()

        # Act
        result = await handler.handle(telegram_update, telegram_context)

        # Assert
        assert result == States.MAIN_MENU
        telegram_update.message.reply_text.assert_called_once_with(
            "Нет активных соревнований"
        )

    @patch("telegram_bot.keyboard.StageModel.objects.filter")
    async def test_handle_stage_exists_no_track_url(
        self, mock_stage_filter, telegram_update, telegram_context
    ):
        """
        Stage найден, но нет track_url → отправляет сообщение.

        Проверяет сценарий:
        - Этап найден
        - У этапа track_url = None или пустая строка
        - Отправляется текстовое сообщение "Нет активных соревнований"
        """
        # Arrange
        mock_stage = MagicMock()
        mock_stage.track_url = None  # ← URL отсутствует

        mock_stage_filter.return_value.afirst = AsyncMock(return_value=mock_stage)

        handler = TrackHandler()

        # Act
        result = await handler.handle(telegram_update, telegram_context)

        # Assert
        assert result == States.MAIN_MENU
        telegram_update.message.reply_text.assert_called_once_with(
            "Нет активных соревнований"
        )


    # TODO: Добавь тест на обработку исключений
    @pytest.mark.parametrize("db_error",[
        DatabaseError,IntegrityError,DataError
        ])
    @patch("telegram_bot.keyboard.logger")
    @patch("telegram_bot.keyboard.StageModel.objects.filter")
    async def test_handle_database_error(
        self, mock_stage_filter,mock_logger,db_error, telegram_update, telegram_context
    ):
        """
        Ошибка базы данных → метод НЕ падает.
    
        Проверяет отказоустойчивость:
        - При возникновении исключения в БД (DatabaseError, IntegrityError, DataError)
        - Метод должен обработать ошибку
        - Должны быть переданные данные в логи
        """
        # Arrange
        mock_stage_filter.return_value.afirst = AsyncMock(side_effect=db_error)

        # Act
        handler = TrackHandler()
        result = await handler.handle(telegram_update,telegram_context)

        # Assert
        assert result == States.MAIN_MENU
        mock_logger.exception.assert_called_once()