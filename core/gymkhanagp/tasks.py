import logging

from asgiref.sync import async_to_sync
from core import celery_app
from telegram_bot.utils.messages import send_telegram_message

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=4,
    default_retry_delay=30,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
    autoretry_for=(Exception,),
)
def send_telegram_message_task(self, telegram_id: int, message: str) -> str:
    # Высылаем сообщение пользователю
    logger.info("Запущена задача по отправке сообщения")
    async_to_sync(send_telegram_message)(telegram_id, message)
    return f"tg_msg: [{telegram_id}]: {message}"
