from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class Report(BaseModel):
    SOURCE_REPORT = {
        "Telegram": "Telegram",
        "Website": "Website",
        "Other": "Other",
    }
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст отчета")
    source = models.CharField(
        max_length=20, choices=SOURCE_REPORT.items(), verbose_name="Источник отчета"
    )

    class Meta:
        verbose_name = "Репорт пользователя"
        verbose_name_plural = "Репорты пользователей"
        ordering = ("-created_at",)
        db_table = "reports"
        default_related_name = "profile"
