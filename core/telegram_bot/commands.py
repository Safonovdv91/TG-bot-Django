import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.manager import KeyboardManager
from telegram_bot.states import States
from telegram_bot.utils.users import create_user_from_telegram
from users.models import SourceReports, TypeReport
from users.utils import ReportHandler, AdminNotifier, get_user_by_telegram_id

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
    text = " ".join(context.args) if context.args else None
    if text is None:
        await update.message.reply_text(
            "Опишите пожалуйста проблему в одном сообщении:"
        )
        context.user_data["state"] = States.BUG_REPORT_WAIT
        return States.BUG_REPORT_WAIT

    user = get_user_by_telegram_id(update.effective_user.id)
    success, message = await ReportHandler.handle_report(
        user=user, text=text, source=SourceReports.TELEGRAM, type_report=TypeReport.BUG
    )

    if not success:
        admin_contact = await AdminNotifier.get_admin_contacts()
        message += f"\nСвяжитесь с администратором: {admin_contact}"

    await update.message.reply_text(message)
    context.user_data["state"] = States.MAIN_MENU
    return States.MAIN_MENU


async def feature_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> States:
    logger.info(f"Feature report: {update.message.text}")

    return States.FEATURE_REPORT_WAIT
