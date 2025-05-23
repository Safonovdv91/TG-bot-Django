# --- Реализации вспомогательных сервисов ---
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Optional, Dict

from g_cup_site.models import StageModel, StageResultModel


class IStageService(ABC):
    """Абстракция для работы с этапами"""

    @abstractmethod
    async def get_active_stage(self) -> Optional[StageModel]:
        pass

    @abstractmethod
    async def get_best_result(self, stage: StageModel) -> Optional[StageResultModel]:
        pass


class TimeConverter:
    """Реализация конвертации временных форматов"""

    def to_milliseconds(self, time_input: Any) -> Optional[int]:
        """Конвертация различных форматов времени в миллисекунды"""
        if isinstance(time_input, (int, float)):
            return int(time_input * 1000)

        try:
            if ":" in time_input:
                minutes, rest = time_input.split(":", 1)
                seconds, milliseconds = rest.split(".") if "." in rest else (rest, 0)
            else:
                minutes = 0
                seconds, milliseconds = (
                    time_input.split(".") if "." in time_input else (time_input, 0)
                )

            return (
                int(minutes) * 60 * 1000
                + int(seconds) * 1000
                + int(milliseconds.ljust(2, "0")[:2])
            )
        except (ValueError, AttributeError):
            return None

    def to_mmssms(self, milliseconds: int) -> Optional[str]:
        """Форматирование миллисекунд в строку MM:SS.MS"""
        try:
            delta = timedelta(milliseconds=milliseconds)
            minutes = delta.seconds // 60
            seconds = delta.seconds % 60
            return f"{minutes:02}:{seconds:02}.{delta.microseconds // 1000:03}"
        except (TypeError, ValueError):
            return None


class ClassCoefficientManager:
    """Управление коэффициентами для классов спортсменов"""

    COEFFICIENTS: Dict[str, float] = {
        "A": 1.00,
        "B": 1.00,
        "C1": 1.05,
        "C2": 1.10,
        "C3": 1.15,
        "D1": 1.20,
        "D2": 1.30,
        "D3": 1.40,
        "D4": 1.50,
        "N": 1.50,
        None: 1.60,
    }

    def get_coefficient(self, sportsman_class: Optional[str]) -> float:
        """Получение коэффициента для класса"""
        return self.COEFFICIENTS.get(sportsman_class, 1.60)


class StageService(IStageService):
    """Сервис для работы с данными этапов"""

    async def get_active_stage(self) -> Optional[StageModel]:
        """Получение активного этапа"""
        active_stage = await StageModel.objects.filter(
            status__in=("judging", "accepting")
        ).afirst()
        return active_stage

    async def get_best_result(self, stage: StageModel) -> Optional[StageResultModel]:
        """Получение лучшего результата для этапа"""
        return await stage.results.order_by("result_time_seconds").afirst()
