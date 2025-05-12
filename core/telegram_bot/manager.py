from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.keyboard import SendTrackHandler, KeyboardActionHandler
from telegram_bot.utils.users import create_user_from_telegram


class KeyboardManager:
    def __init__(self):
        self._handlers = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        # Здесь можно добавлять новые обработчики
        self.add_handler(SendTrackHandler())

    def add_handler(self, handler: KeyboardActionHandler) -> None:
        self._handlers[handler.button_text] = handler

    def get_keyboard(self) -> ReplyKeyboardMarkup:
        buttons = [[handler.button_text] for handler in self._handlers.values()]
        return ReplyKeyboardMarkup(
            buttons, resize_keyboard=True, one_time_keyboard=False
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        text = update.message.text
        handler = self._handlers.get(text)

        if handler:
            await handler.handle(update, context)
        else:
            # Если сообщение не является командой кнопки, обрабатываем как обычное сообщение
            await self._handle_regular_message(update, context)

    async def _handle_regular_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        tg_user = update.effective_user
        user, created = await create_user_from_telegram(tg_user)

        if created:
            await update.message.reply_text(
                "🔐 Вы зарегистрированы!",
                reply_markup=self.get_keyboard(),
            )
        else:
            await update.message.reply_text(
                f"Привет, {user.first_name}! Выберите действие:(кнопка подписки внизу)",
                reply_markup=self.get_keyboard(),
            )
