from django.db import models
from django.contrib.auth import get_user_model

user = get_user_model()


class SourceReports(models.TextChoices):
    TELEGRAM = "Telegram", "telegram"
    WEBSITE = "Website", "website"
    OTHER = "Other", "other"


class TypeReport(models.TextChoices):
    BUG = "Bug", "bug"
    FEATURE = "Feature", "feature"
    OTHER = "Other", "other"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class Report(BaseModel):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст отчета")
    source = models.CharField(
        max_length=20,
        choices=SourceReports.choices,
        verbose_name="Источник отчета",
        default=SourceReports.OTHER,
    )
    report_type = models.CharField(
        max_length=20,
        verbose_name="Тип отчета",
        default=TypeReport.OTHER,
    )
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Репорт пользователя"
        verbose_name_plural = "Репорты пользователей"
        ordering = ("-created_at",)
        db_table = "reports"
        default_related_name = "profile"

    objects = models.Manager()

    def __str__(self):
        return f"Report #{self.id} ({self.report_type})"
