import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.keyboard import (
    SendTrackHandler,
    KeyboardActionHandler,
    SubscriptionKeyboardHandler,
    ClassSelectionHandler,
    BaseClassSelectionHandler,
    BaseClassKeyboardHandler,
)
from telegram_bot.states import States
from telegram_bot.utils.users import create_user_from_telegram

logger = logging.getLogger(__name__)


class KeyboardManager:
    def __init__(self):
        self._handlers = {}
        self._class_selection_handlers = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        # Главное меню
        self.add_handler(SendTrackHandler())
        self.add_handler(SubscriptionKeyboardHandler())
        self.add_handler(BaseClassKeyboardHandler())

        # Меню выбора класса
        self.add_class_selection_handler(ClassSelectionHandler())
        self.add_class_selection_handler(BaseClassSelectionHandler())

    def add_handler(self, handler: KeyboardActionHandler) -> None:
        self._handlers[handler.button_text] = handler

    def add_class_selection_handler(self, handler: KeyboardActionHandler):
        self._class_selection_handlers[handler.__class__.__name__] = handler

    def get_main_keyboard(self) -> ReplyKeyboardMarkup:
        buttons = [[handler.button_text] for handler in self._handlers.values()]
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    def get_keyboard(self) -> ReplyKeyboardMarkup:
        buttons = [[handler.button_text] for handler in self._handlers.values()]
        return ReplyKeyboardMarkup(
            buttons, resize_keyboard=True, one_time_keyboard=False
        )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        handler = None
        text = update.message.text
        current_state = context.user_data.get("state", States.MAIN_MENU)

        if current_state == States.MAIN_MENU:
            handler = self._handlers.get(text)
        elif current_state == States.CLASS_SELECTION:
            handler = self._class_selection_handlers.get("ClassSelectionHandler")
        elif current_state == States.BASE_CLASS_SELECTION:
            handler = self._class_selection_handlers.get("BaseClassSelectionHandler")

        if handler:
            new_state = await handler.handle(update, context)
            context.user_data["state"] = new_state
        else:
            logger.warning(
                "Получено сообщение без статуса. Возвращаем к главному меню."
            )
            context.user_data["state"] = States.MAIN_MENU
            await update.message.reply_text(
                "Главное меню:", reply_markup=self.get_main_keyboard()
            )

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
