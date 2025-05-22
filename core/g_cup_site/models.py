from django.core.exceptions import ValidationError
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
    (None, "None"),
]

STATUS_CHOICES = [
    ("upcoming", "Предстоящий этап"),
    ("accepting", "Приём результатов"),
    ("judging", "Подведение итогов"),
    ("completed", "Прошедший этап"),
    ("canceled", "Этап отменён"),
]

CHAMP_TYPE_CHOICES = [
    ("gp", "Классический чемпионат GGP"),
    ("offline", "Очные соревнования"),
    ("online", "Онлайн-соревнования"),
]


class ChampionshipModel(models.Model):
    """Модель чемпионата"""

    id = models.AutoField(primary_key=True)
    champ_id = models.IntegerField(verbose_name="ID чемпионата")
    title = models.CharField(max_length=255, verbose_name="Название чемпионата")
    year = models.IntegerField(
        validators=[MinValueValidator(1900)], verbose_name="Год проведения"
    )
    description = models.TextField(verbose_name="Описание (HTML)")
    champ_type = models.CharField(
        max_length=20,
        verbose_name="Тип чемпионата",
        choices=CHAMP_TYPE_CHOICES,
        null=True,
        blank=True,
    )

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

    id = models.AutoField(primary_key=True)
    stage_id = models.IntegerField(verbose_name="ID этапа")
    championship = models.ForeignKey(
        ChampionshipModel,
        on_delete=models.CASCADE,
        related_name="stages",
        verbose_name="Чемпионат",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус этапа"
    )
    title = models.CharField(max_length=255, verbose_name="Название этапа")
    stage_class = models.CharField(
        max_length=2, choices=CLASS_CHOICES, verbose_name="Класс этапа"
    )
    track_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка на трассу",
    )
    date_start = models.DateTimeField(verbose_name="Дата начала", null=True)
    date_end = models.DateTimeField(verbose_name="Дата окончания", null=True)

    class Meta:
        verbose_name = "Этап чемпионата"
        verbose_name_plural = "Этапы чемпионатов"
        ordering = ["date_start"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def clean(self):
        if self.date_end and self.date_start and self.date_end < self.date_start:
            raise ValidationError("Дата окончания не может быть раньше даты начала")

    @property
    def description_display(self):
        return mark_safe(self.championship.description)

    objects = models.Manager()


class MotorcycleModel(models.Model):
    """Модель мотоциклов"""

    title = models.CharField(max_length=100, verbose_name="Название мотоцикла")

    class Meta:
        verbose_name = "Мотоцикл"
        verbose_name_plural = "Мотоциклы"

    def __str__(self):
        return f"{self.title}"


class CountryModel(models.Model):
    """Модель стран"""

    title = models.CharField(max_length=100, verbose_name="Название страны")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
        return f"{self.title}"


class CityModel(models.Model):
    """Модель городов"""

    title = models.CharField(max_length=100)
    country = models.ForeignKey(
        CountryModel,
        on_delete=models.CASCADE,
        verbose_name="Страна",
        related_name="cities",
    )

    def __str__(self):
        return f"{self.title}"


class AthleteModel(models.Model):
    """Модель спортсменов на GCup"""

    id = models.IntegerField(primary_key=True, verbose_name="ID спортсмена на сайте")
    first_name = models.CharField(max_length=100, verbose_name="Имя спортсмена")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия спортсмена")
    city = models.ForeignKey(
        CityModel,
        on_delete=models.CASCADE,
        verbose_name="Город",
        related_name="athletes",
    )
    sportsman_class = models.CharField(
        max_length=2, choices=CLASS_CHOICES, verbose_name="Класс спортсмена"
    )
    img_url = models.URLField(
        max_length=500, verbose_name="Ссылка на фото спортсмена", null=True, blank=True
    )
    number = models.IntegerField(verbose_name="Номер спортсмена", null=True, blank=True)

    class Meta:
        verbose_name = "Спортсмен"
        verbose_name_plural = "Спортсмены"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["sportsman_class"]),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class StageResultModel(models.Model):
    """Результаты участников этапа"""

    stage = models.ForeignKey(
        StageModel,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Этап",
    )
    user = models.ForeignKey(
        AthleteModel,
        on_delete=models.CASCADE,
        verbose_name="Спортсмен",
        related_name="results",
    )
    motorcycle = models.ForeignKey(
        MotorcycleModel,
        on_delete=models.CASCADE,
        verbose_name="Мотоцикл",
        related_name="results",
    )
    date = models.DateTimeField(verbose_name="Дата заезда")
    place = models.IntegerField(verbose_name="Место в этапе", blank=True, null=True)
    fine = models.IntegerField(verbose_name="Штраф")
    result_time_seconds = models.IntegerField(verbose_name="Итоговое время (мс)")
    result_time = models.CharField(max_length=20, verbose_name="Итоговое время")
    video = models.URLField(max_length=500, blank=True, null=True, verbose_name="Видео")

    class Meta:
        verbose_name = "Результат этапа"
        verbose_name_plural = "Результаты этапов"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} на {self.stage.title} {self.place} место"


class BaseFigureModel(models.Model):
    """Модель базовых фигур на сайте"""

    id = models.IntegerField(primary_key=True, verbose_name="ID фигуры на сайте")
    title = models.CharField(max_length=255, verbose_name="Название фигуры")
    description = models.TextField(verbose_name="Описание фигуры")
    track = models.URLField(max_length=500, verbose_name="Фото фигуры")
    with_in_class = models.BooleanField(verbose_name="Производится ли повышение класса")

    class Meta:
        verbose_name = "Базовая фигура"
        verbose_name_plural = "Базовые фигуры"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"


class BaseFigureSportsmanResultModel(models.Model):
    base_figure = models.ForeignKey(
        BaseFigureModel,
        on_delete=models.CASCADE,
        related_name="results_base_figure",
        verbose_name="Базовая фигура",
    )
    user = models.ForeignKey(
        AthleteModel,
        on_delete=models.CASCADE,
        verbose_name="Спортсмен",
        related_name="results_base_figure",
    )
    motorcycle = models.ForeignKey(
        MotorcycleModel,
        on_delete=models.CASCADE,
        verbose_name="Мотоцикл",
        related_name="results_base_figure",
    )
    date = models.DateTimeField(verbose_name="Дата заезда")
    fine = models.IntegerField(verbose_name="Штраф", blank=True, null=True)
    result_time_seconds = models.IntegerField(verbose_name="Итоговое время (мс)")
    result_time = models.CharField(max_length=20, verbose_name="Итоговое время")
    video = models.URLField(max_length=500, blank=True, null=True, verbose_name="Видео")

    class Meta:
        verbose_name = "Результат проезда базовой фигуры"
        verbose_name_plural = "Результаты проездов базовых фигур"
        ordering = ["-date"]
