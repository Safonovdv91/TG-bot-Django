from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes


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

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка нажатия кнопки"""
        active_stage = await self._get_active_stage()
        if active_stage and active_stage.track_url:
            await update.message.reply_text(
                text=f"Трасса для этапа '{active_stage.title}':\n{active_stage.track_url}"
            )
        else:
            await update.message.reply_text(
                text="На данный момент нет соревнований в стадии 'Приём результатов'."
            )
