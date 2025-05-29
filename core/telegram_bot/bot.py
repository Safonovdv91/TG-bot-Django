import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from django.conf import settings
from django.contrib.auth import get_user_model

from telegram_bot.commands import start, bug_report, feature_report
from telegram_bot.manager import KeyboardManager
from telegram_bot.states import States

User = get_user_model()
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard_manager = KeyboardManager()
    await keyboard_manager.handle_message(update, context)


def setup_bot():
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    keyboard_manager = KeyboardManager()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, keyboard_manager.handle_message
            )
        ],
        states={
            States.MAIN_MENU: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, keyboard_manager.handle_message
                )
            ],
            States.CLASS_SELECTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, keyboard_manager.handle_message
                )
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    start_handler = CommandHandler("start", start)
    bug_handler = CommandHandler("bug_report", bug_report)
    feature_handler = CommandHandler("feature", feature_report)

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(bug_handler)
    application.add_handler(feature_handler)

    # Обработчик для любых других сообщений
    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            lambda update, context: update.message.reply_text(
                "Пожалуйста, используйте команду /start для начала работы"
            ),
        )
    )

    return application
