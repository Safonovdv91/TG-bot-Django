import logging
from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.manager import KeyboardManager
from telegram_bot.states import States
from telegram_bot.utils.users import create_user_from_telegram


logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None | States:
    keyboard_manager = KeyboardManager()
    tg_user = update.effective_user
    user, created = await create_user_from_telegram(tg_user)
    user_name = tg_user.first_name or user.username
    if created:
        created_message = """
        Радушно приветствую! Бот призван помочь тебе отслеживать данные о спортсменах.
        Основное управление устроено через меню кнопок которые появились в правом нижнем углу.
        Там ты можешь выбрать о каких результатах ты хочешь получать уведомления. На данные момент
        можно получать уведомления о: GGP и Базовые фигуры. Там выбираешь класс - и будешь получать 
        уведомления о всех результатах этого класса.
        Так же если найдешь баг то либо пиши @@SoftikMy или пришли команду /bug_report.
        Если есть крутые идеи по расширению возможностей то пришли команду /feature и комаанда разработки
        приступит к реализации твоей идеи!
        """
        logger.info(f"New user: {user}")
        await update.message.reply_text(
            f"Добро пожаловать, {user_name}!",
            reply_markup=keyboard_manager.get_main_keyboard(),
        )
        await update.message.reply_text(text=created_message)
    else:
        logger.info(f"Existing user: {user}")
        await update.message.reply_text(
            f"Вы уже зарегестрированы, {user_name}!",
            reply_markup=keyboard_manager.get_main_keyboard(),
        )

    context.user_data["state"] = States.MAIN_MENU
    return States.MAIN_MENU


async def bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    logger.info(f"Bug report: {update.message.text}")
    text = update.message.text.strip("/bug_report")[1:]
    if text:
        logger.info(f"Bug report: {text}")
        await update.message.reply_text("Спасибо за багрепорт!")
        return States.MAIN_MENU

    await update.message.reply_text("Введите текст баг-репорта")
    return States.BUG_REPORT_WAIT


async def feature_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    logger.info(f"Feature report: {update.message.text}")

    return States.FEATURE_REPORT_WAIT
