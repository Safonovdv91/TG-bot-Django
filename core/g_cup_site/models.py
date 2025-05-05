from django.db import models
from django.core.validators import MinValueValidator
from django.utils.safestring import mark_safe

CLASS_CHOICES = [
    ("A", "A"),
    ("B", "B"),
    ("C1", "C1"),
    ("C2", "C2"),
    ("C3", "C3"),
    ("D1", "D1"),
    ("D2", "D2"),
    ("D3", "D3"),
    ("D4", "D4"),
    ("N", "N"),
]

STATUS_CHOICES = [
    ("upcoming", "Предстоящий этап"),
    ("accepting", "Приём результатов"),
    ("judging", "Подведение итогов"),
    ("completed", "Прошедший этап"),
    ("canceled", "Этап отменён"),
]


class Championship(models.Model):
    """Модель чемпионата"""

    id = models.IntegerField(primary_key=True, verbose_name="ID чемпионата")
    title = models.CharField(max_length=255, verbose_name="Название чемпионата")
    year = models.IntegerField(
        validators=[MinValueValidator(1900)], verbose_name="Год проведения"
    )
    description = models.TextField(verbose_name="Описание (HTML)")

    class Meta:
        verbose_name = "Чемпионат"
        verbose_name_plural = "Чемпионаты"
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def description_display(self):
        return mark_safe(self.description)


class StageModel(models.Model):
    """Модель этапа чемпионата"""

    championship = models.ForeignKey(
        Championship,
        on_delete=models.CASCADE,
        related_name="stages",
        verbose_name="Чемпионат",
    )
    id = models.IntegerField(primary_key=True, verbose_name="ID этапа")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус этапа"
    )
    title = models.CharField(max_length=255, verbose_name="Название этапа")
    description = models.TextField(verbose_name="Описание (HTML)")
    users_count = models.IntegerField(verbose_name="Количество участников", default=0)
    stage_class = models.CharField(
        max_length=2, choices=CLASS_CHOICES, verbose_name="Класс этапа"
    )
    track_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Ссылка на трассу"
    )
    date_start = models.DateTimeField(verbose_name="Дата начала")
    date_end = models.DateTimeField(verbose_name="Дата окончания")
    reference_time_seconds = models.IntegerField(verbose_name="Эталонное время (мс)")
    reference_time = models.CharField(
        max_length=20, verbose_name="Эталонное время (строка)"
    )
    best_time_seconds = models.IntegerField(
        verbose_name="Лучшее время (мс)", blank=True, null=True
    )
    best_time = models.CharField(
        max_length=20, verbose_name="Лучшее время (строка)", blank=True, null=True
    )
    best_user_id = models.IntegerField(
        verbose_name="ID лучшего спортсмена", blank=True, null=True
    )
    best_user_first_name = models.CharField(
        max_length=100, verbose_name="Имя лучшего спортсмена", blank=True, null=True
    )
    best_user_last_name = models.CharField(
        max_length=100, verbose_name="Фамилия лучшего спортсмена", blank=True, null=True
    )
    best_user_full_name = models.CharField(
        max_length=200,
        verbose_name="Полное имя лучшего спортсмена",
        blank=True,
        null=True,
    )
    best_user_city = models.CharField(
        max_length=100, verbose_name="Город лучшего спортсмена", blank=True, null=True
    )

    class Meta:
        verbose_name = "Этап чемпионата"
        verbose_name_plural = "Этапы чемпионатов"
        ordering = ["date_start"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def description_display(self):
        return mark_safe(self.description)


class GGPSportsmen(models.Model):
    """Модель спортсменов на GCup"""

    id = models.IntegerField(primary_key=True, verbose_name="ID спортсмена на сайте")
    fullName = models.CharField(max_length=255, verbose_name="Полное имя спортсмена")
    firstName = models.CharField(max_length=100, verbose_name="Имя спортсмена")
    lastName = models.CharField(max_length=100, verbose_name="Фамилия спортсмена")
    city = models.CharField(max_length=100, verbose_name="Город спортсмена")
    country = models.CharField(max_length=100, verbose_name="Страна спортсмена")
    sportsman_class = models.CharField(
        max_length=2, choices=CLASS_CHOICES, verbose_name="Класс спортсмена"
    )
    img_url = models.URLField(max_length=500, verbose_name="Ссылка на фото спортсмена")
    number = models.IntegerField(verbose_name="Номер спортсмена", null=True)


class StageGGP(models.Model):
    """Модель этапа GGP (основная модель)"""

    STATUS_CHOICES = [
        ("upcoming", "Предстоящий этап"),
        ("accepting", "Приём результатов"),
        ("judging", "Подведение итогов"),
        ("completed", "Прошедший этап"),
        ("canceled", "Этап отменён"),
    ]

    id = models.IntegerField(primary_key=True, verbose_name="ID этапа")
    champ_id = models.IntegerField(verbose_name="ID чемпионата")
    champ_id = models.ForeignKey(
        Championship, on_delete=models.CASCADE, verbose_name="Чемпионат"
    )
    champ_title = models.CharField(max_length=255, verbose_name="Название чемпионата")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус этапа"
    )
    title = models.CharField(max_length=255, verbose_name="Название этапа")
    description = models.TextField(verbose_name="Описание (HTML)")
    users_count = models.IntegerField(verbose_name="Количество участников", default=0)
    stage_class = models.CharField(
        max_length=2, choices=CLASS_CHOICES, verbose_name="Класс этапа"
    )
    track_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Ссылка на фото трассы"
    )
    date_start = models.DateTimeField(verbose_name="Дата начала")
    date_end = models.DateTimeField(verbose_name="Дата завершения")
    reference_time_seconds = models.IntegerField(verbose_name="Эталонное время (мс)")
    reference_time = models.CharField(max_length=20, verbose_name="Эталонное время")

    class Meta:
        verbose_name = "Этап GGP"
        verbose_name_plural = "Этапы GGP"
        ordering = ["-date_start"]

    def __str__(self):
        return f"{self.champ_title} - {self.title} ({self.get_status_display()})"

    @property
    def description_display(self):
        return mark_safe(self.description)

    def save(self, *args, **kwargs):
        # Конвертация Unix time в DateTime при необходимости
        if isinstance(self.date_start, int):
            self.date_start = datetime.datetime.fromtimestamp(self.date_start)
        if isinstance(self.date_end, int):
            self.date_end = datetime.datetime.fromtimestamp(self.date_end)
        super().save(*args, **kwargs)


class StageResult(models.Model):
    """Результаты участников этапа"""

    stage = models.ForeignKey(
        StageGGP, on_delete=models.CASCADE, related_name="results", verbose_name="Этап"
    )
    user_id = models.ForeignKey(
        GGPSportsmen, on_delete=models.CASCADE, verbose_name="Спортсмен"
    )

    motorcycle = models.CharField(max_length=100, verbose_name="Мотоцикл")
    date = models.DateTimeField(verbose_name="Дата заезда")
    place = models.IntegerField(verbose_name="Место в этапе")
    time_seconds = models.IntegerField(verbose_name="Лучшее время (мс)")
    time = models.CharField(max_length=20, verbose_name="Лучшее время")
    fine = models.IntegerField(verbose_name="Штраф")
    result_time_seconds = models.IntegerField(verbose_name="Итоговое время (мс)")
    result_time = models.CharField(max_length=20, verbose_name="Итоговое время")
    percent = models.FloatField(verbose_name="Процент отставания")
    new_class = models.CharField(
        max_length=2, blank=True, null=True, verbose_name="Новый класс"
    )
    points = models.IntegerField(verbose_name="Баллы")
    video = models.URLField(max_length=500, blank=True, null=True, verbose_name="Видео")

    class Meta:
        verbose_name = "Результат этапа"
        verbose_name_plural = "Результаты этапов"
        ordering = ["place"]

    def __str__(self):
        return f"{self.user_full_name} - {self.place} место"


class PreviousAttempt(models.Model):
    """Предыдущие попытки участника"""

    result = models.ForeignKey(
        StageResult,
        on_delete=models.CASCADE,
        related_name="previous",
        verbose_name="Результат",
    )
    date = models.DateTimeField(verbose_name="Дата попытки")
    time_seconds = models.IntegerField(verbose_name="Время (мс)")
    time = models.CharField(max_length=20, verbose_name="Время")
    fine = models.IntegerField(verbose_name="Штраф")
    result_time_seconds = models.IntegerField(verbose_name="Итоговое время (мс)")
    result_time = models.CharField(max_length=20, verbose_name="Итоговое время")
    attempt_class = models.CharField(max_length=2, verbose_name="Класс")
    video = models.URLField(max_length=500, blank=True, null=True, verbose_name="Видео")

    class Meta:
        verbose_name = "Предыдущая попытка"
        verbose_name_plural = "Предыдущие попытки"
        ordering = ["date"]

    def __str__(self):
        return f"Попытка от {self.date.strftime('%d.%m.%Y')} - {self.time}"
