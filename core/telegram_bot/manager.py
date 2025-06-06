import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from telegram_bot.keyboard import (
    TrackHandler,
    BaseHandler,
    GGPSubscriptionHandler,
    GGPSelectionHandler,
    BaseFigureSubscriptionHandler,
    BaseFigureSelectionHandler,
    TimeTableGGPHandler,
    BugReportHandler,
    FeatureReportHandler,
)
from telegram_bot.states import States
from telegram_bot.utils.users import create_user_from_telegram

logger = logging.getLogger(__name__)


class KeyboardManager:
    def __init__(self):
        self._handlers: dict[str, BaseHandler] = {}
        self._class_selection_handlers = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        # Главное меню
        self.add_handler(TrackHandler())
        self.add_handler(TimeTableGGPHandler())
        self.add_handler(GGPSubscriptionHandler())
        self.add_handler(BaseFigureSubscriptionHandler())

        self.main_menu = ReplyKeyboardMarkup(
            keyboard=[
                [GGPSubscriptionHandler().button],
                [BaseFigureSubscriptionHandler().button],
                [
                    TrackHandler().button,
                    TimeTableGGPHandler().button,
                ],
            ],
            resize_keyboard=True,
        )

        # Меню выбора класса
        self.add_class_selection_handler(GGPSelectionHandler())
        self.add_class_selection_handler(BaseFigureSelectionHandler())
        self.add_class_selection_handler(BugReportHandler())
        self.add_class_selection_handler(FeatureReportHandler())

    def add_handler(
        self,
        handler: BaseHandler,
    ) -> None:
        self._handlers[handler.button_text] = handler

    def add_class_selection_handler(self, handler: BaseHandler):
        self._class_selection_handlers[handler.__class__.__name__] = handler

    def get_main_keyboard(self) -> ReplyKeyboardMarkup:
        return self.main_menu

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        handler = None
        text = update.message.text
        current_state = context.user_data.get("state", States.MAIN_MENU)

        if current_state == States.MAIN_MENU:
            handler = self._handlers.get(text)
        elif current_state == States.CLASS_SELECTION:
            handler = self._class_selection_handlers.get("GGPSelectionHandler")
        elif current_state == States.BASE_CLASS_SELECTION:
            handler = self._class_selection_handlers.get("BaseFigureSelectionHandler")
        elif current_state == States.BUG_REPORT_WAIT:
            handler = self._class_selection_handlers.get("BugReportHandler")
        elif current_state == States.FEATURE_REPORT_WAIT:
            handler = self._class_selection_handlers.get("FeatureReportHandler")
        if handler:
            new_state = await handler.handle(update, context)
            context.user_data["state"] = new_state
        else:
            logger.warning(
                "Получено сообщение без статуса. Возвращаем к главному меню."
            )
            logger.warning(f"Текст сообщения: {text}")
            context.user_data["state"] = States.MAIN_MENU
            await update.message.reply_text(
                "Главное меню: ✔️ 📈 ❌", reply_markup=self.get_main_keyboard()
            )

    async def _handle_regular_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        tg_user = update.effective_user
        user, created = await create_user_from_telegram(tg_user)

        if created:
            await update.message.reply_text(
                "🔐 Вы зарегистрированы!",
                reply_markup=self.get_main_keyboard(),
            )
        else:
            await update.message.reply_text(
                f"Привет, {user.first_name}! Выберите действие:(кнопка подписки внизу)",
                reply_markup=self.get_main_keyboard(),
            )
