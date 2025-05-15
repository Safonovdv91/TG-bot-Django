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

from telegram_bot.manager import KeyboardManager
from telegram_bot.states import States
from telegram_bot.utils.users import create_user_from_telegram

User = get_user_model()
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard_manager = KeyboardManager()
    await keyboard_manager.handle_message(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None | States:
    keyboard_manager = KeyboardManager()
    tg_user = update.effective_user
    user, created = await create_user_from_telegram(tg_user)
    if created:
        created_message = """
        Дорогой друг, к сожалению по некоторым причинам база данных с твоими подписками на классы канула в лету.
        Понимаю тебя, и надеюсь что ты сможешь вспомнить за кем хотел следить и какие классы тебя интересовали больше всего.
        На данный момент я переписан с нуля, и совсем скоро обзаведусь новым и полезным функционалом. тут могут быть небольшие ошибки,
        но они будут исправлены в ближайшее время. и если ты столкнулся с ними - напиши моему хозяину @SoftikMy.
        Ну а вообще не забывай что ты должнен тренироваться - ведь постоянные тренировки и бодрый дух помогут тебе!
        """
        logger.info(f"New user: {user}")
        user_name = tg_user.first_name or user.username
        await update.message.reply_text(
            f"Добро пожаловать, {user_name}!",
            reply_markup=keyboard_manager.get_main_keyboard(),
        )
        await update.message.reply_text(text=created_message)
    else:
        logger.info(f"Existing user: {user}")
        await update.message.reply_text(
            f"Вы уже зарегестрированы, {user.username}!",
            reply_markup=keyboard_manager.get_main_keyboard(),
        )

    context.user_data["state"] = States.MAIN_MENU
    return States.MAIN_MENU


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
    command_handler = CommandHandler("start", start)

    application.add_handler(conv_handler)
    application.add_handler(command_handler)

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
