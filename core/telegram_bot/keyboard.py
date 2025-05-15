import logging
import typing
from abc import ABC, abstractmethod

from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from gymkhanagp.models import (
    UserSubscription,
    SportsmanClassModel,
    Subscription,
    CompetitionTypeModel,
)
from telegram_bot.states import States

logger = logging.getLogger(__name__)


class KeyboardActionHandler(ABC):
    @property
    @abstractmethod
    def button_text(self) -> str:
        pass

    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass


class SendTrackHandler(KeyboardActionHandler):
    """Обработчик для отправки трека"""

    @property
    def button_text(self) -> str:
        return "🗺️ Выслать карту GGP"

    async def _get_active_stage(self):
        from g_cup_site.models import StageModel

        return await StageModel.objects.filter(status="Приём результатов").afirst()

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None | States:
        """Обработка нажатия кнопки"""
        active_stage = await self._get_active_stage()
        if active_stage and active_stage.track_url:
            await update.message.reply_photo(
                photo=active_stage.track_url,
                caption=f"{active_stage.title}\n "
                f"https://gymkhana-cup.ru/competitions/special-stage?id={active_stage.stage_id}",
            )
        else:
            await update.message.reply_text(
                text="На данный момент нет соревнований в стадии 'Приём результатов'."
            )
        return States.MAIN_MENU


class SubscriptionKeyboardHandler(KeyboardActionHandler):
    @property
    def button_text(self) -> str:
        return "📝 Подписаться на GGP классы"

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None | States:
        user = update.effective_user
        social_account = await SocialAccount.objects.filter(uid=str(user.id)).afirst()

        if not social_account:
            # todo Зарегистрировать пользователя
            await update.message.reply_text("Сначала зарегистрируйтесь через /start")
            return States.MAIN_MENU

        subscription, _ = await UserSubscription.objects.aget_or_create(
            user=social_account.user,
            defaults={
                "is_active": True,
                "source": "telegram",
            },
        )
        # Получаем текущие подписки пользователя
        subscribed_classes = await self._get_user_subscribed_classes(subscription)

        keyboard = await self.get_keyboard(subscribed_classes)

        keyboard.append(["🔙 Назад"])

        await update.message.reply_text(
            "Выберите класс спортсмена:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )

        context.user_data["subscription_id"] = subscription.id
        return States.CLASS_SELECTION

    async def _get_user_subscribed_classes(self, subscription):
        return [
            sc.name
            async for sc in SportsmanClassModel.objects.filter(
                subscription__user_subscription=subscription
            ).all()
        ]

    @staticmethod
    async def get_keyboard(subscribed_classes) -> typing.List[typing.List[str]]:
        """Функция для создания клавиатуры, получает все подписки пользователя и формирует клавиатуру"""
        """Асинхронная версия с fallback для старых Django."""
        try:
            # Попытка использовать нативный async (Django 5.0+)
            classes = await SportsmanClassModel.objects.all().alist()
        except AttributeError:
            # #todo какой-то костыльный вариант
            classes = await sync_to_async(list)(SportsmanClassModel.objects.all())
        # Формируем клавиатуру
        keyboard = []
        row = []
        for i, cls in enumerate(classes, 1):
            prefix = cls.subscribe_emoji if cls.name in subscribed_classes else "🔲"
            row.append(f"{prefix} {cls.name}")
            if i % 3 == 0 or i == len(classes):
                keyboard.append(row)
                row = []

        return keyboard


class ClassSelectionHandler(KeyboardActionHandler):
    @property
    def button_text(self) -> str:
        return ""

    async def handle(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None | States:
        text = update.message.text
        if text == "🔙 Назад":
            return await self._handle_back(update, context)

        class_name = text[2:].strip()  # Извлекаем "A" из "🟩 A"
        subscription_id = context.user_data.get("subscription_id")

        if not subscription_id:
            await update.message.reply_text("Ошибка сессии. Начните с /start")
            return States.MAIN_MENU

        try:
            sportsman_class = await SportsmanClassModel.objects.aget(name=class_name)
            subscription = await UserSubscription.objects.aget(pk=subscription_id)

            # Используем правильный асинхронный transaction.atomic
            from django.db import transaction

            try:
                with transaction.atomic():
                    is_subscribed = await Subscription.objects.filter(
                        user_subscription=subscription, sportsman_class=sportsman_class
                    ).aexists()

                    if is_subscribed:
                        await Subscription.objects.filter(
                            user_subscription=subscription,
                            sportsman_class=sportsman_class,
                        ).adelete()
                    else:
                        default_competition = (
                            await CompetitionTypeModel.objects.afirst()
                        )
                        await Subscription.objects.acreate(
                            user_subscription=subscription,
                            sportsman_class=sportsman_class,
                            competition_type=default_competition,
                        )
            except Exception as e:
                logger.error(f"Ошибка транзакции: {str(e)}")
                await update.message.reply_text("⚠️ Ошибка при изменении подписки")
                return States.CLASS_SELECTION

            subscribed_classes = await self._get_user_subscribed_classes(subscription)
            keyboard = await SubscriptionKeyboardHandler.get_keyboard(
                subscribed_classes
            )

            keyboard.append(["🔙 Назад"])

            action = "подписан" if not is_subscribed else "отписан"
            await update.message.reply_text(
                f"Вы {action} на класс {class_name}",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            )

            return States.CLASS_SELECTION

        except SportsmanClassModel.DoesNotExist:
            await update.message.reply_text("Неизвестный класс")
            return States.CLASS_SELECTION
        except Exception as e:
            logger.error(f"Ошибка в ClassSelectionHandler: {str(e)}")
            await update.message.reply_text("⚠️ Произошла ошибка")
            return States.MAIN_MENU

    async def _handle_back(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> States:
        from telegram_bot.manager import KeyboardManager

        keyboard_manager = KeyboardManager()
        await update.message.reply_text(
            "Главное меню:", reply_markup=keyboard_manager.get_main_keyboard()
        )
        return States.MAIN_MENU

    async def _get_user_subscribed_classes(self, subscription):
        return [
            sc.name
            async for sc in SportsmanClassModel.objects.filter(
                subscription__user_subscription=subscription
            ).all()
        ]
