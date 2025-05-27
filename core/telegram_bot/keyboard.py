import logging
import typing
from abc import ABC, abstractmethod
from django.db import transaction
from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from g_cup_site.models import StageModel, StageResultModel
from gymkhanagp.models import (
    UserSubscription,
    SportsmanClassModel,
    Subscription,
    CompetitionTypeModel,
)
from telegram_bot.states import States
from telegram_bot.utils.math_calculate import (
    ClassCoefficientManager,
    StageService,
    TimeConverter,
)
from telegram_bot.utils.messages import MessageTimeTableFormatter
from users.models import SourceReports, TypeReport
from users.utils import get_user_by_telegram_id, ReportHandler

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Базовый класс для обработчиков действий"""

    COMPETITION_TYPE: typing.Optional[str] = None
    STATE: typing.Optional[States] = None

    @property
    @abstractmethod
    def button_text(self) -> str:
        pass

    @property
    @abstractmethod
    def button(self) -> KeyboardButton:
        pass

    @abstractmethod
    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> typing.Optional[States]:
        pass

    @staticmethod
    async def get_keyboard(
        subscribed_classes: typing.List[str],
    ) -> typing.List[typing.List[str]]:
        """Генератор клавиатуры с буквами подпискиподписками"""
        try:
            classes = await SportsmanClassModel.objects.all().alist()
        except AttributeError:
            classes = await sync_to_async(list)(SportsmanClassModel.objects.all())

        keyboard = []
        row = []
        for i, cls in enumerate(classes, 1):
            prefix = cls.subscribe_emoji if cls.name in subscribed_classes else "🔲"
            row.append(f"{prefix} {cls.name}")
            if i % 3 == 0 or i == len(classes):
                keyboard.append(row)
                row = []
        return keyboard

    @staticmethod
    async def _handle_back(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        """Обработка возврата в главное меню, для многоуровневых меню необходимо будет хранить стэк состояний
        а пока это статикметод
        """
        from telegram_bot.manager import KeyboardManager

        await update.message.reply_text(
            "Главное меню:", reply_markup=KeyboardManager().get_main_keyboard()
        )
        return States.MAIN_MENU


class SubscriptionHandlerMixin:
    """Миксин для обработки подписок на спортивные классы"""

    async def _get_user_subscriptions(
        self, subscription: UserSubscription
    ) -> typing.List[str]:
        """Получает список подписок пользователя"""
        return [
            sc.name
            async for sc in SportsmanClassModel.objects.filter(
                subscription__user_subscription=subscription,
                subscription__competition_type__name=self.COMPETITION_TYPE,
            )
        ]

    async def _toggle_subscription(
        self,
        subscription: UserSubscription,
        sportsman_class: SportsmanClassModel,
        competition_name: str,
    ) -> bool:
        """Переключает состояние подписки"""
        with transaction.atomic():
            competition = await CompetitionTypeModel.objects.filter(
                name=competition_name
            ).afirst()
            is_subscribed = await Subscription.objects.filter(
                user_subscription=subscription,
                sportsman_class=sportsman_class,
                competition_type=competition,
            ).aexists()

            if is_subscribed:
                await Subscription.objects.filter(
                    user_subscription=subscription,
                    sportsman_class=sportsman_class,
                ).adelete()
                return False
            else:
                await Subscription.objects.acreate(
                    user_subscription=subscription,
                    sportsman_class=sportsman_class,
                    competition_type=competition,
                )
                return True


class TrackHandler(BaseHandler):
    """Обработчик отправки карты этапа и ссылки на соревнование"""

    @property
    def button_text(self) -> str:
        return "🗺️ Выслать карту GGP"

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        active_stage = await StageModel.objects.filter(
            status__in=("judging", "accepting")
        ).afirst()

        if active_stage and active_stage.track_url:
            await update.message.reply_photo(
                photo=active_stage.track_url,
                caption=f"{active_stage.title}\nhttps://gymkhana-cup.ru/competitions/special-stage?id={active_stage.stage_id}",
            )
        else:
            await update.message.reply_text("Нет активных соревнований")

        return States.MAIN_MENU


class TimeTableGGPHandler(BaseHandler):
    """Обработчик для предоставления временных диапазонов этапа"""

    def __init__(
        self,
    ):
        self.stage_service = StageService()
        self.coefficient_manager = ClassCoefficientManager()
        self.message_formatter = MessageTimeTableFormatter(TimeConverter())

    @property
    def button_text(self) -> str:
        return "Получить 🕗 этапа"

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        """Основная логика обработки запроса"""
        try:
            if not (active_stage := await self.stage_service.get_active_stage()):
                await update.message.reply_text("🏜️ Нет активных соревнований")
                return States.MAIN_MENU

            if not (
                best_result := await self.stage_service.get_best_result(active_stage)
            ):
                await update.message.reply_text("🏜️ Нет результатов для этапа 🏜️")
                return States.MAIN_MENU

            base_time = self._calculate_base_time(best_result)
            sportsman_class: SportsmanClassModel = (
                await SportsmanClassModel.objects.filter(
                    name=best_result.user.sportsman_class
                ).afirst()
            )

            message = f"Лидер: {sportsman_class.subscribe_emoji} {sportsman_class.name} - {best_result.user.full_name}\n"
            message += f"Время: {best_result.result_time}\n"
            message += self.message_formatter.format_time_ranges(base_time)

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Ошибка обработки: {str(e)}")
            await update.message.reply_text("Произошла ошибка при обработке запроса")

        return States.MAIN_MENU

    def _calculate_base_time(self, result: StageResultModel) -> int:
        """Расчет базового времени с учетом коэффициента класса"""
        coefficient = self.coefficient_manager.get_coefficient(
            result.user.sportsman_class if result.user else None
        )
        return int(result.result_time_seconds / coefficient)


class BaseSubscriptionHandler(BaseHandler, SubscriptionHandlerMixin):
    """Базовый обработчик подписок"""

    SELECTION_TEXT: str = "Выберите класс спортсмена:"
    COMPETITION_NAME: str = None

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        user = update.effective_user
        social_account = await SocialAccount.objects.filter(uid=str(user.id)).afirst()

        if not social_account:
            await update.message.reply_text("Сначала зарегистрируйтесь через /start")
            return States.MAIN_MENU

        subscription, _ = await UserSubscription.objects.aget_or_create(
            user=social_account.user, defaults={"is_active": True, "source": "telegram"}
        )

        subscribed_classes = await self._get_user_subscriptions(subscription)
        keyboard = await self.get_keyboard(subscribed_classes)
        keyboard.append(["🔙 Назад"])

        await update.message.reply_text(
            self.SELECTION_TEXT,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

        context.user_data["subscription_id"] = subscription.id
        return self.STATE


class GGPSubscriptionHandler(BaseSubscriptionHandler):
    """Обработчик подписки на GGP классы"""

    COMPETITION_TYPE = "ggp"
    STATE = States.CLASS_SELECTION
    SELECTION_TEXT = "Выберите класс спортсмена:"
    COMPETITION_NAME = "ggp"

    @property
    def button_text(self) -> str:
        return "📝 Подписаться на GGP классы"

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)


class BaseFigureSubscriptionHandler(BaseSubscriptionHandler):
    """Обработчик подписки на базовые фигуры"""

    COMPETITION_TYPE = "base"
    STATE = States.BASE_CLASS_SELECTION
    SELECTION_TEXT = "Выберите базовый класс:"
    COMPETITION_NAME = "base"

    @property
    def button_text(self) -> str:
        return "📝 Подписаться на Базовые фигуры"

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)


class BaseSelectionHandler(BaseHandler, SubscriptionHandlerMixin):
    """Базовый обработчик выбора класса"""

    COMPETITION_NAME: str = None
    ACTION_TEXT_SUBSCRIBED = "подписаны на класс"
    ACTION_TEXT_UNSUBSCRIBED = "отписаны от класса"

    @property
    def button_text(self) -> str:
        return ""

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        text = update.message.text
        if text == "🔙 Назад":
            return await self._handle_back(update, context)

        return await self._process_class_selection(update, context)

    async def _process_class_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        class_name = update.message.text[2:].strip()
        subscription_id = context.user_data.get("subscription_id")

        if not subscription_id:
            await update.message.reply_text("Ошибка сессии. Начните с /start")
            return States.MAIN_MENU

        try:
            sportsman_class = await SportsmanClassModel.objects.aget(name=class_name)
            subscription = await UserSubscription.objects.aget(pk=subscription_id)

            is_subscribed = await self._toggle_subscription(
                subscription, sportsman_class, self.COMPETITION_NAME
            )

            await self._update_interface(
                update, subscription, is_subscribed, class_name
            )
            return self.STATE

        except SportsmanClassModel.DoesNotExist:
            await update.message.reply_text("Неизвестный класс")
            return self.STATE
        except Exception as e:
            logger.error(f"Ошибка в {self.__class__.__name__}: {str(e)}", exc_info=True)
            await update.message.reply_text("⚠️ Произошла ошибка")
            return States.MAIN_MENU

    async def _update_interface(
        self,
        update: Update,
        subscription: UserSubscription,
        is_subscribed: bool,
        class_name: str,
    ):
        subscribed_classes = await self._get_user_subscriptions(subscription)
        keyboard = await self.get_keyboard(subscribed_classes)
        keyboard.append(["🔙 Назад"])

        action = (
            self.ACTION_TEXT_SUBSCRIBED
            if is_subscribed
            else self.ACTION_TEXT_UNSUBSCRIBED
        )
        await update.message.reply_text(
            f"Вы {action} - {class_name}",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )


class BugReportHandler(BaseHandler):
    @property
    def button_text(self) -> str:
        return "Отправить 🐞 баг-репорт"

    @property
    def button(self) -> KeyboardButton:
        return KeyboardButton(self.button_text)

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        user = get_user_by_telegram_id(update.effective_user.id)
        text = update.message.text
        success, message = await ReportHandler.handle_report(
            user=user,
            text=text,
            source=SourceReports.TELEGRAM,
            type_report=TypeReport.BUG,
        )
        if success:
            await update.message.reply_text("Успешно зарегестрирован баг-report 🐞")
            return States.MAIN_MENU

        await update.message.reply_text(message)
        return States.BUG_REPORT_WAIT


class GGPSelectionHandler(BaseSelectionHandler):
    """Обработчик выбора GGP класса"""

    COMPETITION_TYPE = "ggp"
    STATE = States.CLASS_SELECTION
    COMPETITION_NAME = "ggp"
    ACTION_TEXT_SUBSCRIBED = "подписаны на GGP класс"
    ACTION_TEXT_UNSUBSCRIBED = "отписаны от GGP класса"


class BaseFigureSelectionHandler(BaseSelectionHandler):
    """Обработчик выбора базового класса"""

    COMPETITION_TYPE = "base"
    STATE = States.BASE_CLASS_SELECTION
    COMPETITION_NAME = "base"
    ACTION_TEXT_SUBSCRIBED = "подписаны на базовый класс"
    ACTION_TEXT_UNSUBSCRIBED = "отписаны от базового класса"
